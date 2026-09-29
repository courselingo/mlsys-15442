# 事实核对 · mlsys-15442 第 21 讲 Mega-Kernel
- 核对人：非作者
- 核对日期：2026-09-29
- 被核对版本：content/21-mega-kernel/index.md，归一化 SHA256 前16 = `AC35096F69C374D4`（全文 19,068 B）
- 源材料：`_sources/mlsys-15442/evidence/mlsys-slide-19-mega-kernel.pdf.faithful.txt`（28,634 B；**211 个 NUL 字节** ⇒ `read` 按二进制拒读，改用逐行读取）+ 原件 `mlsys-slide-19-mega-kernel.pdf`（**目视渲染**，pypdfium2 5.13.0，scale=3）
- 抽取器与锚词（按说明第 ② 条先试探）：抽取器 = `.faithful.txt`（本课程规定）。
  锚词 `Mega` / `Mirage` / `MPK` / `Kernel` / `Task` / `Event` 全部命中 ⇒ **本文件没有逐字符错位**（`Task graph is a "lower-level" CUDA graph` 在 faithful 里是 `7DVN JUDSK LV D ³ORZHU - OHYHO´ &8'$ JUDSK`——**只有这一页（PDF p14 / 块 14）局部错位**，我用原件目视核过它的页脚与副标题）。**没有** kern 把词切碎到不可检索。
- ⚠️ **块数 = PDF 页数 = 36，但页脚编号到 39**：`===== PAGE =====` **36 块**，原件 `pdfium` 实测 **36 页**，而页脚数字最大到 **39**。
  用 `pypdfium2` 逐页读页脚定出：**块 k ↔ PDF 第 k 页**（k≥2 成立），但**页脚 7、9、10、16、23 这五页在 faithful 里没有对应文本块**（正文丢失）。
  ⇒ 本记录一律用「**幻灯片标题 + 逐字原文**」定位；其中 **PDF p16（页脚 19，`Compiler Workflow #1`）是丢失页**，我改用**原件目视**核了它的全部三条 bullet（见 P1-1）。

## 结论
P0（事实错误）：**2** 条 ｜ P1（易误解/依据不足）：**4** 条 ｜ P2（措辞）：**4** 条

## P0 · 事实错误

| # | 位置 | 正文说 | 源材料说 | 依据（逐字引用 + 幻灯片标题） |
| --- | --- | --- | --- | --- |
| P0-1 | 正文第 46 行；配图 `figures/mega-kernel-3.svg`（第 4 行 `desc`、第 1857 行与第 2817 行文字） | 「课件指出**两点**。一是内核之间的**屏障**让跨层的流水线做不起来……二是**它**也让细粒度的重叠做不起来。**两条的根源是同一个**。」 | 课件 `Limitations` 一共列了**三点**，而且**前两点的成因是分开写的、不是同一条**：`No Inter-Layer Pipelining — Kernel barriers prevent inter-layer pipelining`；`No Overlapping — Coarse-grained dependency prevents comp. & comm. overlap`；`Limited Dynamism — Rely on CUDA graphs to reduce kernel launch overhead`。⇒ ① 少认了一点（**Limited Dynamism**）；② 把第二点的成因从 **`Coarse-grained dependency`** 错说成「内核屏障」。 | 幻灯片标题 `Limitations`（PDF p7，**目视**页脚为 `8`；faithful 块 7 逐字为 `Limitations \| No Inter - Layer Pipelining \| Kernel barriers prevent inter - layer pipelining \| No Overlapping \| Coarse - grained dependency \| prevents comp. & comm. overlap \| Limited Dynamism \| Rely on CUDA graphs to reduce \| kernel launch overhead`）。**原件目视**（`pdfpage7.png`）确认同页还有一张对照图：`NanoFlow: Towards Optimal Large Language Model Serving Throughput, OSDI'24`（该标签在 faithful 里是错位字形 `1DQR)ORZ…`，我用原件读出）。⇒ 页面写的「两个限制」与源的三点不符，「同一条边界造成的两种后果」这一因果归纳也**不是课件的说法**。 |
| P0-2 | 正文第 196 行（以及第 26 行） | 「这也是**这门课最后一讲**的合适落点。」（第 26 行：「这一讲也是**全课的收束**」） | **本课最后一讲是第 21 讲**，不是第 19 讲。第 8 讲溯源第 219–220 行的全表把它钉死：`…；第 19 讲 ← advanced-topic-mlc（无编号）；第 20 讲 ← 18-kernel-superoptimization；第 21 讲 ← 19-mega-kernel`；仓库里也确实有 `content/21-mega-kernel/`（`lecture = 21`）。而**第 21 讲自己**写着「这是这门课 21 讲的最后一讲」（`content/21-mega-kernel/index.md` 第 192 行）。⇒ 两讲都自称「最后一讲」，第 19 讲那一句是事实错误（且在同一页出现了两次）。 | `content/08-transformer-attention/index.md` 第 219–220 行全表；`content/21-mega-kernel/index.md` 第 192 行。另核课件：第 19 讲的源（`mlsys-slide-advanced-topic-mlc.pdf`，57 页）**末页是 `Ongoing directions`**（faithful 块 57 逐字 `Across Multiple Services, Contexts \| Ongoing directions \| … \| Efficient tensor compiler abstractions \| … \| Open source`），**课件里没有「这是最后一讲」这类收束语** ⇒ 那句话是我们编排时写的，而编排与全表冲突。 |

## P1 · 易误解或依据不足

| # | 位置 | 正文说 | 问题 | 依据 |
| --- | --- | --- | --- | --- |
| P1-1 | 正文第 128 行 | 「第一步……**前者**决定任务有多大，**后者**决定任务怎么连。」（只讲了切法与插入同步事件两件事） | 源的第一步有**三条** bullet，第三条被整段漏掉：`Generate high-performance CUDA implementation for each task`。这一条恰恰是「每个任务要生成 CUDA 实现」，与后文「运行期只做轻量调度」是配套的；漏掉后读者会以为第一步只产出图、不产出代码。 | 幻灯片标题 `Compiler Workflow #1: Operator Decomposition & Dependency Analysis`（**PDF p16，faithful 丢失页**，改用**原件目视**）。该页逐字为：`• Optimize operator-to-task decomposition based on available SMs` / `• Add synchronization events to capture precise task dependencies` / `• Generate high-performance CUDA implementation for each task`。faithful 里该页块只有标题行（`Compiler Workflow #1: \| Operator Decomposition & Dependency Analysis`），三条 bullet 全无。 |
| P1-2 | 正文第 48 行 | 「课件的图把这两个限制画在**一条时间轴**上：**张量内存、张量核心、CUDA 核心**各自都有活，但内核的边界把它们切成一段一段，中间留出空隙。」 | **机器对了一部分，说法错了**：源确实有这三条泳道（`Tensor Memory Accelerator` / `Tensor Cores` / `CUDA Cores`），但它们画的是**两条并列的泳道组**——左栏 `Kernel 1` / `Kernel 2`（各自内部标 `Pipeline bubbles`），右栏一条 `Fused Kernel`（无气泡）——是**两张泳道图的对比**，不是「一条时间轴上被切成一段一段」。 | 幻灯片标题 `Limitations`（PDF p5，faithful 块 5 逐字）：`Limitations \| Tensor Memory \| Accelerator \| Tensor Cores \| CUDA Cores \| Kernel 1 \| Kernel 2 \| Pipeline \| bubbles \| Pipeline \| bubbles \| No Inter - Layer Pipelining \| Kernel barriers prevent inter - layer pipelining \| Tensor Memory \| Accelerator \| Tensor Cores \| CUDA Cores \| Fused Kernel`。 |
| P1-3 | 正文第 96 行 | 「运行期按这张图把任务分给各个 worker 执行，**自己不做分析**。」 | 源 `MPK Overview` 页只有两侧的框与其输入输出（`LLM` / `MPK Compiler` / `Task graph` / `MPK Runtime` / `Serving config (batching, paging, speculative decoding, etc)` / `User requests`），**没有一句**说运行期「不做分析」。这是页面从「编译期重、运行期轻」这一对比里推出来的，但被摆在陈述课文的位置。 | 幻灯片标题 `MPK Overview`（PDF p12，faithful 块 12 逐字 `MPK Overview \| LLM \| MPK \| Compiler \| Task graph \| MPK \| Runtime \| Serving config (batching, paging, \| speculative decoding, \| etc \| ) \| User requests`）。检索 `analy` / `analyze` / `analysis` 于该页 → 0。 |
| P1-4 | 正文第 160 行 | 「这个循环里**没有「查询全局状态」这一步**，所以它可以一直转下去。」 | 源的两类循环都写得很具体（worker：`Fetch a task from its queue` / `Execute the task` / `Trigger the completion event`；scheduler：`Dequeue fully triggered event` / `Launch all tasks depending on the event`），但**没有**「不查询全局状态」这条描述。页面把「去中心化调度」这一条**从后面那一页挪到前面**当成了循环本身的性质。 | 幻灯片标题 `Task-Based Parallel Runtime`（PDF p23，faithful 块 23 逐字）；去中心化调度在**另一页**：`Techniques to Minimize Task Launch Overhead`（PDF p31，faithful 块 31）逐字 `Lightweight workers and schedulers \| Task & event queues: circular buffers on device memory \| Event notification, task enqueue/dequeue: atomic operations \| Decentralized scheduling \| Schedulers assign tasks using only local information \| Hybrid task launch \| …`。 |

## P2 · 措辞

| # | 位置 | 正文/配图 | 说明 |
| --- | --- | --- | --- |
| P2-1 | 正文第 164 行 | 「它同时列出了降低任务启动开销的**四条**手段：轻量的 worker 与 scheduler、……、原子操作……、以及去中心化的调度。」 | 源该页列了 **6 条 bullet**：`Lightweight workers and schedulers` / `Task & event queues: circular buffers on device memory` / `Event notification, task enqueue/dequeue: atomic operations` / `Decentralized scheduling`（+子条 `Schedulers assign tasks using only local information`）/ **`Hybrid task launch`**（+子条 `Compiler classifies each op as AOT/JIT based on runtime load balance`、`Ahead-of-time: launched before event trigger to reduce latency`、`Just-in-time: launched after event trigger to balance load`）。页面**整条漏掉 `Hybrid task launch`**（这不是措辞，是内容缺口，但因页面明写「四条」而源为五类、且漏的那条有自己的子机制，我按 P2 记并在此说明）。 |
| P2-2 | 正文第 24 行 | 「课件先回顾了内核的基本单位……而「**Mega**」指的是把这些内核合并成一个。」 | 源的标题是 `What is a (Mega-)Kernel?`，**带括号与连字符**，且该页只画了 `GPU Kernel` / `Thread block` / `Thread` / `Device Memory` / `SM` 的层次结构，**没有一句文字定义「Mega」=合并**。页面把标题的构词法当成了课件的定义。另：源该页的 `Tensor Memory Accel.` 单元页面未提。 |
| P2-3 | 正文第 60、62 行 | 「Mega-Kernel 里没有内核屏障，整个模型**在一次启动里跑完**」「『没有内核屏障』……**是这一讲全部好处的来源**」 | 源 PDF p9 把 `✓ No kernel barriers` 与 `✓ Operator reordering`、`✓ Load balancing` 并列为三个卖点（块 8 逐字 `No kernel barriers \| 9 \| Operator reordering \| 9 \| Load balancing \| 10 \| … \| An LLM forward pass launches 100s - 1000s kernels`），`Advantages of Mega-Kernel` 页则给 `Inter-Layer Pipelining` / `Overlapping Comp/Comm` / `Dynamic Workloads` 三条。「全部好处的来源」把三个并列项压成一条因果链，源没有这句话。 |
| P2-4 | 正文第 172 行 | 「某个模型每个 token 的延迟从 14.5 毫秒降到 12.5 毫秒」 | 数字**全部正确**，但源点名了模型：`Reducing **Qwen3-8B** per-token latency from 14.5ms to 12.5ms`；页面写成「某个模型」，读者无法回源。同理第 172 行后句「它把这个差距从四点五毫秒压到了二点五毫秒」是我们自己的换算（10−14.5=4.5、10−12.5=2.5，算术无误），**课件没有这组差值**，且溯源第 197 行的推论清单未登记这条换算。 |

## 我核不到的（诚实记录）

- **`Compiler Workflow` 总览页（PDF p15 / 页脚 18）在 faithful 里整段丢失**（块 15 只剩标题行 `Compiler Workflow \| 18`），我改用原件目视确认它**只是一个过渡页**（无子弹文字）。因此「五步」这个计数我只能从 `#1`～`#5` 五个编号页（PDF p16、p17、p18、p19、p20）数出来——**这五步我逐页核到了**（见下）。**但**正文第 146–154 行把第五步与第四步合在同一节（「第四步与第五步：归一化与线性化」），而把第二节写成「**两种事件融合**」覆盖 `#2` 与 `#3` ⇒ 全篇**没有**逐条列出五个步骤的编号清单，读者按「五步」去数会数到 4 个小节。**溯源第 196 行**却写「四是**五步编译流程**」，与正文的 4 个小节对不上（建议补一句「其中第二、三步合为一节讲」）。五步逐字依据：`Compiler Workflow #1: Operator Decomposition & Dependency Analysis`（p16）/ `#2: Successor-Set Fusion`（p17）/ `#3: Predecessor-Set Fusion`（p18）/ `#4: Graph Normalization`（p19）/ `#5: Graph Linearization`（p20）——**编号 `#1`～`#5` 逐页目视确认**。
- **正文第 76 行**「这四件事恰好是第 14 讲与第 16 讲的主题」：四件事里 `Continuous batching` / `paged/radix attention` 我核到在**第 14 讲**（其 `source_title` 逐字含 `Continuous Batching, PagedAttention, RadixAttention`），`speculative decoding` 核到在**第 16 讲**（`source_title` 逐字含 `Speculative Decoding`，其源 `mlsys-slide-15-LLM-serving-part2.pdf` 里 `Speculative Decoding` 命中 47 行）。**但 `prefill/decode`（预填充与解码）这一件我找不到以它为主题的那一讲**——第 8 讲有「预填充阶段/解码阶段」的对比但不是主题，第 14 讲的源里我只确认了连续批处理与两种注意力。⇒ 记为**部分核不到**：三分之四有依据，`prefill/decode` 属于哪一讲我无法确认。
- **正文第 110 行**「第 12 与第 13 讲的分块是为了让一个内核跑得快」：**第 12、13 讲的源都是网页版**（`data_layout`、`gemm`），**不在** `_sources/mlsys-15442/evidence/` 里 ⇒ 我无法回源，不下对错结论。
- **正文第 152 行**「规整带来的收益在**第 12 讲**讲布局时出现过一次」：同上，第 12 讲无源件，**核不到**。
- **溯源第 197 行**「把事件融合与**第 5 讲**的循环变换」联系起来：第 5 讲在仓库里是 `05-optimizing-linear-algebra`，其源件是 `mlsys-slide-05-hardware-acceleration.pdf`（我核到它 24 页、标题页逐字 `Hardware Acceleration`）。我在该 deck 全文检索 `loop transformation` / `Loop` → **0 命中**（`tile the j dimension by` 有一处，属分块）。⇒ 「第 5 讲的循环变换」这一指路**我核不到**（可能指的是第 12 讲那类循环变换，但 12 讲无源件）。**请注意这条与本节其他「核不到」不同：它是有源件、检索了却找不到。**
- **`[[term:...]]` 词条**不在本讲页面的核对范围内，我未核对词条定义。
- **数字逐项回源结果**（全部命中）：`14.5ms` / `12.5ms` / `10ms`（PDF p32 逐字 `Reducing Qwen3 - 8B per - token latency from 14.5ms to 12.5ms \| Approaching theoretical bound of 10ms`）；`100s - 1000s kernels`（PDF p8 逐字 `An LLM forward pass launches 100s - 1000s kernels`）；`a few dozen lines of Python code to mega-kernelize an LLM`（PDF p11）；`outperform existing systems by 1.2 - 6.7x`（PDF p11，页面未引用该数字）；`Each worker runs on one SM / Each scheduler runs on one warp`（PDF p22 逐字）；`Techniques…` 六条（PDF p31）；两个 Open Questions（PDF p34 `How to decompose layers into tasks?` + `Currently rely on heuristics + profiling-based tuning` / PDF p35 `How to schedule tasks across workers?` + `no synchronization with workers` / `load imbalance`）。✔

## 覆盖面

- **配图：14 张**（`mega-kernel-1.svg` … `-14.svg`，与正文 14 处 `![...]` 一一对应，无游离图）。
  - **逐张通读：14 张全部**（`grep '<desc|<text '` 逐条读出 `desc` 与全部 `<text>` 节点）。本讲 P0-1 的直接触发点就是 `-3.svg` 的 `desc` 与两处 `<text>`（「两个限制」「根源是同一个」），而 `desc` **不渲染**——只靠看正文发现不了。
  - **定向检索：0 张**。
- **原件目视**（pypdfium2 渲染，产物在**课程仓库之外**：`D:\Vibe_Workspace\_scratch_mlsys21\img21\`）：第 7、9、16、34、35 页，共 **5 页**；另用 `pypdfium2` 逐页读**全部 36 页的页脚数字**（不渲染），据此定出「块 k ↔ PDF 第 k 页」与**五页正文丢失**（页脚 7/9/10/16/23）。
- **否定性结论的范围与检索词**（faithful 全文，逐行 UTF-8 解码 + NUL 替换）：
  - 「运行期不做分析」：`analy` / `analyze` / `analysis` → 0。
  - 「循环里不查询全局状态」：`global` / `query` / `poll` → 0。
  - 「two limitations / 两个限制」：`Limitations` 命中仅 3 处（PDF p5/p6/p7 的标题），**三点并列的 bullet 命中 3 个不同短语**。
  - 「第 5 讲循环变换」：在 `mlsys-slide-05-hardware-acceleration.pdf.faithful.txt` 里 `loop transformation` / `Loop` → 0。
- **跨讲承诺（第 ⑩ 条）**：
  - **本讲对别人许的承诺：0 条。** `第 2[2-9] 讲` / `下一讲` 全库 0 命中；本讲是末讲 ⇒ **不存在指向第 22 讲之后的空头承诺**。
  - **别人对本讲的承诺：0 条。** 全库检索 `第 21 讲|Mega` 后逐条排除同名词：第 10 讲那两处是 `Megatron-LM`；第 18 讲那四处是 `MegaBlocks`；第 8 讲那处是**课件号对照表**（`第 21 讲 ← 19-mega-kernel`），不是内容承诺。⇒ 本讲**没有被谁承诺过内容**，也就无所谓兑现。
  - **第 13 讲曾对第 20 讲许过承诺**（`content/13-ml-compiler-gemm/index.md` 第 194 行逐字「第 20 讲要讲的内核超优化，走的就是这条线……」），**第 20 讲已兑现**（其正文「Mirage 的核心想法」「抽象表达式」两节正是搜索空间那条线）。这不在我的三讲范围内，附记备查。
  - **「换出/offload」缺口**：本讲与换出无关。faithful 全文检索 `offload` / `swap` / `pinned` / `host` / `cpu` → **hits = 0**。⇒ 本讲**没有**补上第 2 讲对第 11 讲许下的那个承诺，也**没有**对换出许新承诺。全库检索 `换出` 只命中三处（第 2 讲第 204、237 行；第 11 讲第 212 行），**都只是把这处缺口说清楚，没有任何一处补上它** ⇒ 你转述的「课程级缺口」在本课定稿范围内**确认成立、且无例外**。
