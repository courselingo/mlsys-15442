# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 14 讲 LLM 服务技术（上）：连续批处理、PagedAttention 与 RadixAttention

- 核对人：**非作者**（独立核对；作者 `mlsys-author` 未参与，未提问、未改正文）
- 核对日期：2026-09-29
- 被核对版本：`content/14-llm-serving-1/index.md`
  归一化 SHA256 前16 = **19CE87F66D89FD37**（19,742 B）
  - 14 张配图（哈希入档，例：`-3 769C6EB079822EE8`、`-5 43BE9F608E9662D2`、`-13 096F8ECE027EB6FF`）
- 源材料：

| # | 文件 | 用途 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-14-LLM-serving-part1.pdf.faithful.txt`（25,493 B，44 页） | **主要依据**（`.faithful.txt`；本课不用 `text-clean`） |
| 2 | 同 PDF 本体（`mlsys-slide-14-LLM-serving-part1.pdf`） | **渲染了 3 页做图级核验**（见下「方法」） |
| 3 | `_sources/mlsys-15442/evidence/mlsys-slide-15-LLM-serving-part2.pdf.faithful.txt` | 核正文 L232「两讲互不重叠」这句 |

### 方法（本讲多做了一步，请 Lead 留意）

第 14 讲的正文有多处**关于「图上画了什么」**的主张，而文本层只留下列标签、拿不到版面结构。
⇒ 我在**不改任何 `content/`** 的前提下，用 `pypdfium2` 把 **3 页渲染成 PNG** 逐张目视核对（这是本讲能定 P0 的关键）：

| 渲染页 | 文件 | 用来定 |
| --- | --- | --- |
| 第 24 页（PagedAttention 定义页） | `_tmp_l14p24.png`（2112×1188） | **P0-1**（图上到底是几个进程） |
| 第 35 页（Opportunity: KV Cache Reuse） | `_tmp_l14_p35_opportunity.png` | **P0-2**（课件列举的第三类场景是什么） |
| 第 36/37/38 页（RadixAttention 演示） | `_tmp_l14_radix3.png`（三页竖排） | **P1-1**（几页演示） |
| 第 10 页（Continuous Batching + Orca 出处） | `_tmp_l14_p10_orca.png` | 「三处外部材料」的第一处与年份 |

> 复现命令（临时依赖装在 `_tmp_libs/`，不在课程仓库里，未污染 `courses/mlsys-15442`）：
> `python -c "import sys;sys.path.insert(0,r'_tmp_libs');import pypdfium2 as pdfium;pdfium.PdfDocument(<pdf>)[23].render(scale=2.2).to_pil().save('p24.png')"`
> **★ 一个文本层的事实（给 Lead）**：这份 faithful **不是全干净** —— 第 10 页 Orca 出处的后半句（`Based Generative Models, OSDI'22`）
> 与第 22 页的一行（`space of memory to the request's maximum`）是**逐字节 +0x1D 位移的字形码**（`%D V H G` → `Based`），
> 正是 `eth-ca` 记录里描述过的那个现象。**这两行按正常写法检索会 0 命中**，但可用 +0x1D 解出来（我已解码并核对）。
> 其余页面未发现位移。

---

## 结论

**P0（事实错误）：2 条 ｜ P1（易误解/依据不足）：1 条 ｜ P2（措辞）：2 条**

---

## P0 · 事实错误

### P0-1 正文 L146「**三个**进程各自的地址空间是连续的」——课件那张图上只有 **两个**进程（`Process A`、`Process B`）

- **正文 L146**：「课件用一张进程与物理页的对照图来说明这件事：**三个进程**各自的地址空间是连续的，
  而它们真正的物理页交错分布。把这张图里的「进程」换成「请求」、把「页」换成「块」，就是 PagedAttention 的全部机制。」
- **源（第 24 页 `PagedAttention`，★ 我渲染成图逐字看过）**：左半面板标题 `Memory management in OS`，
  画的是 **两个圆 = Process A、Process B**，它们各指向 `Physical Memory` 里的 `Page 0`–`Page 4`；
  右半面板标题 `PagedAttention`，画的是 **两个圆 = Request A、Request B** 与 `KV Cache` 里的 `KV Block 0`–`KV Block 4`。
  文本层同样只有两个进程标签（`Process` + `A` / `Process` + `B`，faithful L1709/1711 与 L1713/1715），
  **全文 `Process` 作为图标签只出现两次**（另一处 `Request A`/`Request B` 同理）。
- **为什么算 P0**：「三个」是一个**关于源图的计数断言**，读者无从复核（图在被引论文里，本页未转载）；
  句子本身通顺，机制（页交错分布 → 换成块）也照旧成立，正是「讲错了也看不出来」的那一类。
- **建议修**：「课件用一张进程与物理页的对照图……」→ 改成「**两个**进程（图中 A、B）」，
  或干脆去掉数目：「课件用一张进程与物理页的对照图……」。

### P0-2 正文 L186 把课件列举的**第三类**场景写成「需要反复引用同一段材料的结构化程序」——课件第 35 页列的是 **(c) Self-consistency（自一致性）**

- **正文 L184–186**：「课件先指出现在的做法：一个请求结束，它的 KV 缓存就被丢掉了。可是很多请求之间共享着同一段前缀，
  比如同一个系统提示词，或者同一段被反复引用的上下文。这类共享在实际负载里非常多。**课件列举的场景包括少样本示例、
  多轮对话的历史、以及需要反复引用同一段材料的结构化程序。**」
- **源（第 35 页 `Opportunity: KV Cache Reuse`，★ 我渲染成图逐字看过）**：三块面板，标题分别是
  ```
  (a) Multi-turn chat      —— Turn 1(Q)/Turn 1(A) … Turn 4，Chat History 逐轮变长
  (b) Few-shot learning    —— Prompt 1/2/3 共用同一段 Few-shot examples
  (c) Self-consistency     —— 一个 Prompt/Question 分叉出 Answer 1/2/3 → Generation 1/2/3
  ```
  ⇒ 课件列举的第三类是 **self-consistency（同一 prompt 采样多次、共享同一段前缀）**，
  不是「需要反复引用同一段材料的结构化程序」；本页**从头到尾没有提到 self-consistency**。
- **它为什么读起来毫无破绽**：「结构化程序（structured language model programs）」恰好是被引论文标题里的词
  （`SGLang: Efficient Execution of Structured Language Model Programs`，faithful L2681）——**归属被论文标题污染了**；
  而「多次引用同一段材料」也确实是一种前缀复用，所以句子自洽。
  （补一句公平话：第 36–38 页的演示帧里确实出现了 `What …/When …/How …`、`This is …/Let us …/We can …/To solve …`
  这类**多分支**的前缀树，所以「结构化」这层意思在课件里不是无中生有；错的只是**「列举的场景」这一句的第三项**。）
- **建议修**：把第三项改成「**自一致性（self-consistency）**：同一个问题采样多次，共享同一段 prompt」；
  若要保留「结构化程序」，需另起一句并说明它出自 SGLang 论文/后面的演示帧，而不是这张列举图。

---

## P1 · 易误解或依据不足

### P1-1 正文 L192「课件用**两页**演示了带前缀共享的注意力计算」——源是 **三页**（第 36、37、38 页，帧 (1)–(9) 连成一段）

- **正文 L192**：「课件用**两页**演示了带前缀共享的注意力计算。」
- **源**：标题 `RadixAttention: Attention with Prefix Sharing` 的页共 **三页**，页脚页码 36 / 37 / 38，
  每页正文都是同样两条 bullet（`Existing systems: discard KV cache after a request finishes` /
  `RadixAttention: maintain an LRU cache for all requests in a radix tree (compact prefix tree)`），
  下面是**同一段动画的 9 帧**：(1)–(5) 在第 36 页、(6)–(7) 在第 37 页、(8)–(9) 在第 38 页（★ 三页我都渲染看过，
  帧号连续、树逐步长大并出现 `evicted`）。
- ⇒ 「两页」与源对不上（少了一页）。这与本讲「三处外部材料」那个计数不同：后者我核了是**三**，是页面写对了。
- **建议修**：「课件用**三页**（帧 1–9）演示了……」。**严重度**：只影响「用了几页」这个外部描述，不改变机制，
  按 l12/l13 同族条目（结构性计数）口径记 P1。

---

## P2 · 措辞

### P2-1 四处「机制级展开」是页面补的，溯源 L231 的推论清单没有列

| 位置 | 页面说 | 源里有的 |
| --- | --- | --- |
| L38 | 「**预填充是计算密集的，解码是访存密集的**，前者关心算力，后者关心带宽」 | 第 4/5 页只有 `Pre-filling phase (first iteration): Process all input tokens at once` / `Decoding phase (all other iterations): Process a single token…`。**全文检索 `bound|bandwidth|compute|memory|latency|throughput|arithmetic`：没有 compute-bound / memory-bound 这类说法**（这句话本身是对的，四大推理引擎文献里的常识，但它不是课件的说法） |
| L136 | 「这 20% 到 40% **不是某个实现写得不好，而是「按最大长度预留」这个策略本身的下限**。换一个实现，只要策略不变，浪费的比例就在同一个量级」 | 第 23 页只有 `Significant Memory Waste in KV Cache` + `Only 20-40% of KV cache is utilized to store actual token states`（**没有**「不是实现问题」这句） |
| L150 | 「[[term:kernel]] 里按块取数据这件事也因此**不需要额外的拷贝步骤**」 | 第 27 页只有 `1. Fetch non-contiguous KV blocks using the block table` / `2. Apply attention on the fly`（「不需要拷贝」是从 `on the fly` 推出来的） |
| L106 | 「如果能提前知道每个请求要生成多长，那么按长度分配就够了，**分页这套机制也就不必要**」 | 第 22 页只有 `Internal fragmentation due to unknown output length`（因果是页面补的） |

⇒ 溯源 L231 目前列了三组共 8 条推论；以上 4 处按同一标准也应补进去（内容多数成立，**不必删**）。

### P2-2 溯源 L232「两份 PDF……**内容也不重叠**」在主题层面成立，但 part2 有一页与 part1 同名同图

- **正文 L232**：「本讲与第 16 讲的关系：两份 PDF 是各自独立的课件（part1 与 part2），页码各自从 1 开始，**内容也不重叠**，因此没有做切分。」
- **核到的事实**：页码各自从 1 开始 ✅（part1 最后一页页码 45。part2 首页页码 1、共 45 页）。
  **主题**不重叠 ✅（part1 = 连续批处理 / PagedAttention / RadixAttention；part2 = Speculative Decoding）。
  但 **part2 的第 2 页**标题是 `Generative LLM Inference: Autoregressive Decoding`，
  与 **part1 第 4/5 页**同名，且都带同一张 `[Accelerating LLM requires machine learning systems optimizations]` + `[EOS]` + `Iter` 铺垫图
  ⇒ **有一页重复的铺垫内容**。
- **建议改法**：把「内容也不重叠」改成「**主题不重叠**（各自有一页同名的自回归解码铺垫页）」，与 cuda-programming-2 那条「两讲不重叠」的处理保持同一口径。
- **严重度**：只影响溯源对两讲关系的描述，正文结论不动 ⇒ P2。

---

## 已核对通过（逐条附页码 + 逐字引用）

> ★ 本讲被点名的核验对象是**「三处外部工作」的归属与计数** —— 我把 44 页里**所有出处脚注都枚举了一遍**，结论是**三处，写对了**：

| 正文 | 源 | 结果 |
| --- | --- | --- |
| **溯源 L229 说「课件在这一讲里引了**三处**外部材料」** | 全文枚举 `slides from` / `Slides from` / `OSDI` 等脚注：**只有三个不同的外部作品** —— `Orca: …`（第 10 页，1 页）、`slides from vllm: …`（faithful L1637/1667/1744/1918/2062/2179/2299/2429/2565，共 **9 页**，覆盖第 22–33 页）、`* Slides from SGLang: …`（L2676/2712/2748/2784/2854/2878/2934/2976 共 **8 页**） | ✅ **计数「三处」正确** |
| 溯源 L229 第一处：**连续批处理那一节引的是 Orca（A Distributed Serving System for Transformer-Based Generative Models）** | 第 10 页脚注（★ 渲染确认）：`Orca: A Distributed Serving System for Transformer-Based Generative Models. OSDI'22` | ✅ **名称逐字对，且挂在连续批处理那一页**（同页 bullet 是 `Higher GPU utilization` / `New requests can start immediately`）。**年份**：源上写 `OSDI'22`，**页面没有引年份**，所以不存在年份配错；若要补年份，应写 **OSDI'22**。（这一行在文本层是 +0x1D 位移码，解码后与渲染一致） |
| 溯源 L229 第二处：**KV 缓存利用率那一页引的是 vLLM（Efficient Memory Management for Large Language Model Serving with PagedAttention）** | 第 23 页：`Significant Memory Waste in KV Cache` + `Only 20-40% of KV cache is utilized to store actual token states` + 脚注 `slides from vllm: Efficient Memory Management for Large Language Model Serving with PagedAttention` | ✅ **名称逐字对**（源写小写 `vllm`，无年份）；**归属对**（20–40% 就在这一页） |
| 溯源 L229 第三处：**RadixAttention 与 CPU 开销那几页引的是 SGLang（Efficient Execution of Structured Language Model Programs）** | 脚注出现在第 35–45 页：`Opportunity: KV Cache Reuse`(35)、RadixAttention(36/37/38)、`CPU Overhead Hiding`(39)、`Overlapped Scheduler`(41)、`Overlapped Scheduling in SGLang`(42)、`Resolve Dependency`(43) 全部带 `* Slides from SGLang: Efficient Execution of Structured Language Model Programs` | ✅ **名称逐字对，且「与 CPU 开销那几页」这个范围也对** |
| L128 课件引 vLLM 的数字：KV 缓存里真正用来存 token 状态的只有 **20% 到 40%** | 第 23 页逐字：`Only 20-40% of KV cache is utilized to store actual token states` | ✅ **逐字**（含「存 token 状态」这层限定） |
| L34 预填充是第一次迭代、一次处理完全部输入 token；解码是其余每一次迭代、每步只生成一个 token | 第 5 页逐字：`Pre-filling phase (first iteration): Process all input tokens at once` / `Decoding phase (all other iterations): Process a single token generated from previous iteration` | ✅ 逐字 |
| L100 KV 缓存要留着：后面每一步都要读全部前缀 | 同页：`Use attention keys & values of all previous tokens` / `Key-value cache: Save attention keys and values for the following iterations to avoid recomputation` | ✅ 逐字（注：源自己就有独立小节 `Key-value cache:`，本页把它挂在第 8 讲上，**没有**说成「我们的提法」，未犯第 8 讲 P1-1 那类错） |
| L50 三个数字：半精度下服务 175B GPT-3 至少要十块 A100-40GB；生成 256 个 token 约 20 秒；没法并行处理很多请求 | 第 15 页逐字：`LLMs are Slow and Expensive to Serve` + `At least ten A100-40GB GPUs to serve 175B GPT-3 in half precision` + `Generating 256 tokens takes ~20 seconds` + `Cannot process many requests in parallel` | ✅ **三项（含「半精度」「GPT-3」）全对** |
| L62 静态批处理的**三个**问题 | 第 9 页 `Batching Requests to Improve GPU Performance` + `Issues with static batching:` + `Requests may complete at different iterations` / `Idle GPU cycles` / `New requests cannot start immediately` | ✅ **三个逐条对应**（`idle GPU cycles` = 「GPU 空转周期」） |
| L76 连续批处理的两条收益 | 第 10 页 `Continuous Batching` + `Benefits:` + `Higher GPU utilization` / `New requests can start immediately` | ✅ 逐字 |
| L82 课件用了**五页**演示连续批处理；L86 五个请求 R1–R5 的到达/结束次序 | `Continuous Batching Step` 共 **5** 页（faithful L725/775/828/890/960）；事件标签逐字：`Receives two new requests R1 and R2` / `Iteration 1: decode R1 and R2` / `Receive a new request R3; finish decoding R1 and R2` / `Iteration 2: decode R1, R2, R3; receive R4, R5; R2 completes` / `Iteration 3: decode R1, R3, R4` | ✅ **五页对**；R1–R5 的次序也对（R2 在第 2 轮完成并离开） |
| L114 做法：提前分配一整块连续内存，**按它能生成的最大长度**算 | 第 22 页：`Pre-allocates contiguous space of memory to the request's maximum length`（该行是位移码，+0x1D 解码后如此；渲染可见） | ✅ 逐字 |
| L116/L120 两笔碎片：内部碎片来源是「输出长度未知」，外部碎片来源是「各请求上限不一致」 | 同页逐字：`Memory fragmentation` / `Internal fragmentation due to unknown output length` / `External fragmentation due to non-uniform per-request max lengths`；图上 `External frag.` / `Internal frag.` 分开画 | ✅ 逐字（L118「两笔分开画」也对） |
| L142 课件的定义：给 KV 缓存做**应用层**的分页与虚拟化 | 第 24 页 bullet（★ 渲染确认）：`Application-level memory paging and virtualization for KV cache` | ✅ 逐字（`Application` / `-` / `level…` 只是 kern 分段） |
| L148 块的定义：一块固定大小、连续的内存，按顺序存放 KV | 第 25 页：`Paging KV Cache Space into KV Blocks*` + `KV block is a …`（同页 `block 0`–`block 7`、`Block size = 4`） | ✅ 定义与页标题对（「块大小」在源里是 4，页面**没有**引这个数，只说它是可调旋钮 ✅ 不算漏） |
| L158 两步：用块表取出不连续的块；在算注意力时即时使用它们 | 第 27 页逐字：`1. Fetch non-contiguous KV blocks using the block table` / `2. Apply attention on the fly` | ✅ 逐字 |
| L160 关键前提：注意力满足**结合律与交换律** | 第 27 页逐字：`Key insight: attention is associative and commutative` | ✅ 逐字 |
| L168 内部碎片只剩最后一个块；**外部碎片完全消失** | 第 33 页逐字：`Minimal internal fragmentation` / `Only happens at the last block of a sequence` / `# wasted tokens per request < block size` / `No external fragmentation` | ✅ 逐字（含 `No external fragmentation`） |
| L170 课件结论「每个请求浪费的 token 数小于块大小」 | 同页：`# wasted tokens per request < block size` | ✅ 逐字 |
| L184 现有做法：请求结束后 KV 缓存就被丢掉；新做法用 LRU + 基数树（紧凑前缀树） | 第 36 页逐字：`Existing systems: discard KV cache after a request finishes` / `RadixAttention: maintain an LRU cache for all requests in a radix tree (compact prefix tree)` | ✅ 逐字 |
| L202 一个没优化好的推理引擎可能有一半以上时间花在 CPU 调度上 | 第 39 页逐字：`An unoptimized inference engine can waste more than 50% time on CPU scheduling` | ✅ 逐字 |
| L204 调度器每一轮的**五件事** | 第 40 页 `Understanding CPU Overhead` / `CPU scheduler iteratively` + 1.`Receives input messages from users` 2.`Processes results from the model worker` 3.`Checks stop conditions` 4.`Runs prefix matching and request reorder` 5.`Allocates memory for the next batch` | ✅ **五条逐条对应** |
| L206 `run_batch` 是**非阻塞**的；重叠对象是 GPU 的 `run_batch` 与 CPU 的 `process_batch_result` | 第 42 页逐字：`Goal: overlap run_batch (GPU) and process_batch_result (CPU)` + `run_batch is non-blocking and returns a reference; overlapping run_batch of the current iteration with process_batch_result of the previous iteration` | ✅ 逐字（★ 这里 `non`/`-`/`blocking` 是**换行断字**，不是「blocking」，我按渲染与上下文两处对照确认过） |
| L210 解法是延迟一次停止条件检查；代价是多算一个没用的 token | 第 43 页逐字：`Key idea: delay the finish condition check` / `We assume a request did not finish and immediately run it in the next decoding batch` / `We resolve dependency by paying the overhead of decoding one more useless token` | ✅ 逐字 |
| L24 大纲三条：连续批处理、PagedAttention、RadixAttention | 第 7 页 outline 三条同名 | ✅ 逐字 |
| L160/L212 跨讲归属：第 8 讲 Flash-Decoding 用结合律交换律；第 9、10 讲讲通信优化 | 仓库编号 08=transformer-attention（其溯源写明 Flash-Decoding 的三步与「结合律交换律」这条前提）、09/10=ml-parallelization 1/2 | ✅ 两处归属一致 |

**跨讲承诺（规则⑩）**：
1. 本讲对别讲的**承诺**：只找到对第 16 讲的**独立性声明**（L232，已按 P2-2 核过），
   以及 L194/L206 里对第 8 讲、第 9/10 讲的**回指**（都是回指，不是承诺）。
   反向检索（`第 14 讲`、`下一讲`、`后面几讲`）命中的也都是回指 —— **没有别讲给本讲许下未兑现的承诺**。
2. 反向证据：第 16 讲溯源 L218 说「**第 14 讲引的三处外部材料**与本讲引的五处不同」——
   与我这次枚举出的「三处」**一致** ✅。

---

## 我核不到的（诚实记录）

1. **第 8 页的时间线图**：文本层只有 `LLM Decoding Timeline` / `Prefill tokens` / `Decode tokens`，
   正文 L38「左边一段是预填充，很短；右边是很长一串解码步」是**对版面的描述**，我**没有渲染这一页** ⇒ 未目视验证。
   （检索词 `Prefill|Decode|Timeline`；同页无其他文字。）
2. **正文 L86 对五页演示逐页画面的描述**（「课件的每一页都在图里标出两件事」）：
   我核到的是**页数（5）与事件标签文字**，**没有**逐页目视确认「请求池」与「执行引擎」两块版面；
   这五页我**没有渲染**。
3. **正文 L136「换一个实现，浪费比例在同一量级」之外的一般性结论**、以及 L52/L134 那些「系统问题/值得搬过来」的定性判断：
   属于页面自己的判断（溯源 L231 已声明其中一部分），我**不判对错**。
4. **没有第二份独立抽取可比**：本讲 PDF 的 `.embedded.txt` 不存在（本课该文件是字体二进制，本讲连它都没有缓存），
   所以交叉验证只有 faithful + 我这次的**渲染图**两路。
5. **位移码范围我没有做全量扫描**：我确认了第 10 页与第 22 页各有一行 +0x1D 位移（可解码），
   但**没有**逐行检查 44 页里还有没有别的位移行 ⇒ 任何「某词在 faithful 里 0 命中」的结论都带这个保留。
   （检索词：`slides from|Slides from|OSDI|Orca|vllm|SGLang|bound|bandwidth|Process`。）

---

## 覆盖面（附录十二）

- **正文**：232 行**逐行读完**；14 张配图**全部文本层通读**（脚本抽每张 SVG 的可见 `<text>` 与 `<title>/<desc>`）。
  `-3`（三个数字）、`-4`（静态批处理三问题）、`-5`（连续批处理收益+出处）、`-7`（KV 一直长）、`-8`（两笔碎片）、
  `-9`（20–40%）、`-10`（分页定义）、`-11`（两步 + 结合律交换律）、`-12`（两种碎片改善）、`-13`（LRU/基数树）、
  `-14`（CPU 开销）、`-1`/`-2`/`-6` 均与正文一致 ✅。
- **源**：faithful 44 页**逐页标题 + 逐字**核过（含全部出处脚注枚举）；
  **另渲染 6 页目视**（第 10、24、35、36、37、38 页；其中 36–38 是三页竖排成一张看帧号连续性）。
- **未验**：上面「我核不到的」1–5。

---

**核对人声明**：本记录只覆盖开头那个哈希的版本（`19CE87F66D89FD37`）。对其它版本的结论不成立。
本记录只读正文、不修改任何 `content/` 文件；渲染产物与临时依赖都在**课程仓库之外**（`_tmp_l14*.png`、`_tmp_libs/`）；
`status` 由 Lead 处理。
