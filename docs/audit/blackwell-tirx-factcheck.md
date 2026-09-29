# 事实核对 · CMU 15-442/15-642 第 15 讲 Blackwell GPU 与 TIRx

- 核对人：非作者
- 核对日期：2026-09-29
- 被核对版本：`content/15-blackwell-tirx/index.md`，归一化 SHA256 前16 = **D0E7FE2D3F3E8ADC**
- 源材料（我实际依据的文件）：
  - `_sources/mlsys-15442/evidence/mlsys-deck-tirx.html`（14,285 B；本讲是网页版 reveal.js，**主页面只有小节标题与 iframe 标签，没有任何正文段落**）
  - 主页面 `iframe src="demo/*.html"` 指向、且已缓存的 10 个演示页：`evidence/tirx/sm_architecture.html`、`pipeline_arch.html`、`tcgen05_intro.html`、`mbarrier_mechanism.html`、`phase_tracking.html`、`why_cuda_ptx_native.html`、`however_cuda_cpp_painful.html`、`step7_principle.html`、`step9_principle.html`、`summary_journey.html`
  - 交叉讲引用另用：`content/13-ml-compiler-gemm/index.md`、`content/14-llm-serving-1/index.md`、`content/06-cuda-programming-1/index.md`、`content/09-ml-parallelization-1/index.md`
- 抽取器与锚词（三步动作）：本讲源是 **HTML，直接读，无 faithful/embedded 之分**。
  - 锚词 `Tensor Core (tcgen05)`（`sm_architecture.html` 命中）、`228 KB per SM`（命中）、`From 0.02 to 1322 TFLOP/s`（命中，**只在 `summary_journey.html`**）、`deterministic operator dispatch`（命中，在 `however_cuda_cpp_painful.html`）。
  - 反向验证：**在主页面 `mlsys-deck-tirx.html` 里检索 `228` / `1322` / `0.02` 命中 0** —— 全部数字都在被 iframe 的演示页里，读主页面本身核不到任何数。

## 结论

P0（事实错误）：**2** 条 ｜ P1（易误解/依据不足）：**6** 条 ｜ P2（措辞）：**5** 条

## P0 · 事实错误

| # | 位置 | 正文说 | 源材料说 | 依据（逐字引用 + 幻灯片标题） |
| --- | --- | --- | --- | --- |
| 1 | `index.md` 第 50 行（「GEMM 的数据通路」），同一错误另见第 34 行（「一个 SM 里有什么」） | 「这条通路比第 13 讲见过的长。**多出来的两级是张量内存与 TMA 引擎**」（第 34 行作「和前面几讲见过的 SM 相比，多出来的**是张量内存与 TMA 引擎**」） | 第 13 讲已经把 TMA 讲透，并把 TMA 画成端到端通路的**第一级** | 第 13 讲页面 `content/13-ml-compiler-gemm/index.md`：小节标题「## TMA：一条指令搬一整块」；「## 端到端的数据通路」下逐字：「数据通路是：**TMA** 把全局内存里的分块搬进共享内存，张量核心从共享内存里读出两块做乘加，结果写进 C。」其源亦是第 13 讲课件缓存页 `evidence/gemm/tma_copy.html`、`evidence/gemm/tma_3d.html`、`evidence/gemm/gemm_endtoend.html`。第 15 讲这边 TMA 的两级出现在 `pipeline_arch.html`：「GMEM →(TMA load)→ SMEM →(tcgen05.mma)→ TMEM →(tcgen05.ld)→ Reg cast →(store)→ SMEM →(TMA store)→ GMEM」 | 
| 2 | 配图 `figures/blackwell-tirx-4.svg` 第 29 行（**渲染在图上**的可见文字） | 「它解决的是寄存器压力问题，这一点在**第 14 步**的收益里会再提一次」 | 全篇只有**十步**，不存在第 14 步 | `summary_journey.html`：`<p class="sub">From 0.02 to 1322 TFLOP/s in 10 steps of TIRx</p>`，其 `steps` 数组恰好 10 项（Step 1 = 0.02 … Step 10 = 1322）；本页正文亦写「一共十步」（第 184 行）。而「十步走完的收益」正是 **图 14**（`blackwell-tirx-14.svg` 标题「十步走完的收益」）⇒ 这是把**图号当成了步号**（判据 ⑧）。文字应是「图 14 的收益」或「第 10 步的收益」。影响小（读者找不到第 14 步），但它是图上的一句陈述 |

> P0-1 的措辞说明：第 13 讲页面与第 13 讲的源两处都表明 TMA 已在第 13 讲讲过 ⇒ 「多出来的两级」至少有一处归属是错的；按本讲正文自己写明的比较基准（「比第 13 讲见过的长」），错在本讲。真正相对第 13 讲新增的只有**张量内存（TMEM）**一级（`sm_architecture.html`：「Tensor Memory (TMEM) — **New in Blackwell**」）。

## P1 · 易误解或依据不足

1. **「第 4 步之后紧接着的必然是第 7 步 …… 这两步的先后关系不是教学上的编排，而是技术上的依赖」**（第 150 行）
   - 源：`summary_journey.html` 的 `steps` 数组里，**Step 5 = 'Software pipeline (4096³)' 639 TFLOP/s**、**Step 6 = 'Persistent kernel (4096³)' 723 TFLOP/s** 就夹在 4 与 7 之间；而课件 outline 只走 1/4/7/9 四站（主页面 `<li>Step 1 — Sync GEMM</li>`、`<li>Step 4 — TMA Async</li>`、`<li>Step 7 — Warp Specialization</li>`、`<li>Step 9 — 2-CTA Cluster</li>`）。
   - ⇒ 4→7 的跳站**恰恰是课件的教学编排**，与正文「不是教学上的编排」相反。读者会以为第 5、6 步不存在。
2. **「[[term:throughput]] 的提升在这里来自重叠」**（第 164 行）—— 与课件自己的数字相抵，详见下面「★ 两组互相约束的证据」节。
3. **「每一步都留了可运行的版本」**（第 186 行；`blackwell-tirx-14.svg` 第 29 行同句）
   - 源只给 **4 步**标了演示：`summary_journey.html` 的 `demo` 字段为 `true` 的是 **Step 1 / 4 / 7 / 9（⭐）**，其余六步为 `false`；页脚原文是 `<strong>Next:</strong> Assignment — Build your own GEMM kernel step by step (10 steps, incremental testing)`，说的是**作业要让读者自己走十步**，没有「十步都留了可运行版本」这句。我在缓存范围内找不到依据（未缓存的 17 个演示页见「我核不到的」）。
4. **「「127」这个数字来自一个 warp 有 32 个线程、而 TMA 只需要一个线程发指令这个事实的推广」**（第 148 行）
   - 源只给结论、不给推导：`summary_journey.html` 卡片 `<div class="card-desc">Let hardware do the work, free 127 threads</div>`；`sm_architecture.html` 的 TMA 详情是「Dedicated DMA engine that copies tensor tiles between **HBM** and **Shared Memory**. **Only 1 thread dispatches**」。从 32 线程推不出 127（32−1=31）；127 = 128−1，与 warp 大小 32 无关。正文把一条**源里没有的推导**写成了陈述句。
5. **「这一点和上一讲的描述符是同一个思路」**（第 70 行）
   - 「上一讲」按讲次是**第 14 讲 `llm-serving-1`**，该讲页面全篇检索 `描述符` **0 命中**；描述符与布局在第 **12/13** 讲，本页第 74 行自己也写「第 12 讲那套布局记号」。⇒ 指路指错了一讲（判据 ④）。
6. **「课件的演示把这一点画成了两条交替的时间线：生产者到达、消费者等待、相位翻转，然后下一轮重复」**（第 100 行）
   - 我在缓存范围内能读到的 `phase_tracking.html` 是**一条 8 格的相位行**（`Iter 0 phase = 0` … `Iter 7 phase = 1`）加一段三步时序（「1 Producer arrives at barrier (phase 0) / 2 Consumer calls `try_wait(phase=0)` — unblocks / 3 Barrier flips to phase 1, `phase ^= 1`」），**不是两条时间线**。生产者/消费者时间线那几页（`mbarrier_arrive_timeline.html`、`mbarrier_tma_timeline.html`、`mbarrier_tcgen05_timeline.html`）**未缓存**，所以我只能记「依据不足」，不下否定结论。

## P2 · 措辞

1. 「**课件分两半**」（第 24 行）—— 课件 outline 是**七节**（Blackwell Programming Model / TIRx Programming Model / Step 1 / Step 4 / Step 7 / Step 9 / Summary），正文自己在下一段也承认「把两半连起来的是……十步路径」，即实为三块。
2. 「**最后一步的目标**是对齐 cuBLAS」（第 186 行；`blackwell-tirx-14.svg` 第 25 行「最后一步的目标 / 对齐 cuBLAS」）—— 源把 `match cuBLAS` 挂在 **2SM Cluster（第 9 步）** 那张卡上（`summary_journey.html`：「2SM Cluster / 2× compute per SMEM tile, match cuBLAS」），而十步里最后一步是 **Step 10 'Multi-consumer (4096³)'**。「最后一步」在本页与源里指的不是同一步。
3. 「**每一步只改一件事**」（第 26 行；`blackwell-tirx-10.svg` 第 29 行「而每一步只改一件事」）—— 源只有 `(10 steps, incremental testing)`，没有「每步只改一件事」这个更强的说法。
4. 「**三组人**各自按通知行事」（第 164 行）、fig-12「TMA、矩阵乘、写回**各由一组 warp** 负责」—— 源的时间线轨道标签是 `TMA — WG1 / warp3`、`MMA — WG1 / warp0`、`Writeback — WG0`：是**两个 warpgroup、三个 warp**，「三组人 / 每组一组 warp」把它说大了。
5. **溯源的证据清单漏了自己要用的一页**（第 206 行）—— 溯源列了 9 个嵌入页（「SM 架构、GEMM 数据通路、tcgen05 与张量内存、MBarrier、相位追踪、原生级访问的动机、双 CTA 簇、warp 专用化、十步总结」），**漏了 `however_cuda_cpp_painful.html`**，而正文「TIRx 给的三个机制」一节的三个机制与「人 / 智能体两类使用者」**逐字出自这一页**。

## 判据 ⑧⑨⑩（这一轮新立的，逐条查）

**⑧ 两套并存的计数/编号体系 —— 本讲有，且未说明换算。**

- 课件的**两套编号**并存：① outline 里带编号的只有 **1 / 4 / 7 / 9** 四站（四个演示小节）；② `summary_journey.html` 的图表是完整的 **1–10** 十步（含只出现在图上的 Step 2/3/5/6/8/10）。
- 正文只用了「十步」这套体系（第 184 行「一共十步」、`blackwell-tirx-14.svg`「从 0.02 到 1322 TFLOP/s，十步」），**从没告诉读者课件的 outline 只走四站**；于是第 150 行「第 4 步之后紧接着的必然是第 7 步」在读者眼里成了「十步里的第 4 步和第 7 步紧邻」，而图上它们之间还有两步（见 P1-1）。
- 还叠加了第三套编号：**图号**。P0-2（「第 14 步」）就是图号与步号混用。建议把「十步里的四站（1/4/7/9）」这句话补进正文。

**⑨ 少认了源材料（把源自己的话标成「我们的提法」）—— 命中 2 条，都在溯源。**

- 溯源第 207 行：「这类推论分三组。一组是因果判断：……**把张量内存的收益归成「派发只需一个线程」这一前提**……」——「派发只需一个线程」**是课件自己的话**：`summary_journey.html` 卡片「tcgen05.mma: Tensor Memory / **TMEM avoids register pressure, single-thread dispatch**」；`sm_architecture.html` 的 tc 详情「**Single thread issues MMA**; HW distributes across 128 lanes.」。
- 溯源第 207 行：「还有一组是关于方法的判断：**把相位机制解释成「等的是哪一轮」**……」——这正是课件的原句：`phase_tracking.html`「Phase tracking solves the problem of "**did this barrier fire for iteration i or iteration i-1?**"」，其代码块注释 `try_wait(tma_bar, phase_tma)` / `phase_tma ^= 1  # flip`。
- ⇒ 溯源把两条**源的原文**划进了「CourseLingo 的讲解」。**正文**反而是对的（第 60 行「课件在最后总结时点出了它的价值」、第 94 行「课件的原话是：这一次触发的是第 i 轮的屏障」）——所以这是**正文与溯源不一致**，而溯源正是署名归属的凭据。
- 反向提示（不算错，但语义被削弱）：溯源把「把第 7 步的收益归因于重叠」也列为我们的因果判断，而 `step7_principle.html` 的副标题就是「Dedicated roles for load / compute / writeback — **maximize hardware utilization**」，源本身是把收益归给重叠的；叠加 P1-2 后，这句归属两头都不牢。

**⑩ 跨讲承诺 —— 本讲对外 0 条承诺；别人对本讲的引用有 1 条在本讲找不到落点。**

- 本讲发给他讲的承诺：**无**（全文的「后面」都指本讲内部，如第 62 行「这是后面 warp 专用化能成立的前提」）。
- 别人对本讲的引用（逐条回到本讲检查）：
  - 第 20 讲 `content/20-kernel-superoptimization/index.md` 第 50 行「**第 15 讲讲过两个 SM 组成簇**」→ ✅ 本讲有（「## 第 9 步：把两个 SM 连起来」）；第 112 行「**第 15 讲的 228 KB**」→ ✅ 有（第 34 行、`sm_architecture.html`「228 KB per SM」）。
  - 第 19 讲 `content/19-advanced-ml-compilation/index.md` 第 72/74 行「**第 15 讲讲 TIRx 的动机时，说的正是同一件事**」→ ✅ 有（「## 为什么需要原生级访问」；`why_cuda_ptx_native.html` 页标题「AI workloads and hardware outpace DSL adaptation and maintenance.」）。
  - 第 16 讲 `content/16-llm-serving-2/index.md` 第 172 行「**第 15 讲讲的那种「由静态到动态」的演进**，在这里又出现了一次」→ ⚠️ **本讲找不到落点**：本讲的源与正文里没有「由静态到动态」这条演进线（最接近的只有未缓存的演示文件名 `pipeline_dynamic.html`）。另外第 16 讲第 217 行把「上一讲」用于第 14 讲的内容（复制与切分），说明**第 14/15/16 讲的「上一讲」指代在仓库里已经不稳**——这不在本讲正文里，留给 Lead 判断。
- 排序：`git log` 里本讲的提交在三讲的核对之前，故此处只报，不改。

## ★ 两组互相约束的证据（按作业要求顺手互验）

**结论：本讲确实有这种结构，而且两组数互相矛盾；正文把它们当同一个故事讲了。**

- **甲组（`step7_principle.html`，微基准）**：`total-bar.seq { width: 100% }` 对 `total-bar.pip { width: 73% }`；左边时间线「Before (Step 4): Sequential」是 11 格（`L k=0 M k=0 L k=1 M k=1 … L k=4 M k=4` + `WB`），右边「After (Step 7): Pipelined」的 makespan 是第 2 列到第 9 列 = 8 格 ⇒ **8/11 = 72.7% ≈ 73%**。这一组**自洽**（我按格的坐标算的，不是目测）；备注里那句「Load and compute are serialized — hardware idle 50% of time」也与 1:1 交替的 11 格一致。
- **乙组（`summary_journey.html`，整核扫描）**：Step 4 = **330**（2048³）、Step 6 = **723**（4096³）、Step 7 = **603**（4096³）、Step 10 = **1322**（4096³）。
- **互验**：若甲组的 73% 就是乙组第 4→7 步之比，则第 7 步应为 330 / 0.73 ≈ **452 TFLOP/s**，而乙组写的是 **603**。两组对不上，因为甲组是「第 4 步的小 tile（5 个 K 步）」的微基准、乙组是**不同问题规模**（2048³ vs 4096³）的整核扫描。
- **更要紧的一条**：乙组里 **Step 6 = 723 > Step 7 = 603，且两者同为 4096³**（同规模、可比）⇒ 课件自己的图表把第 7 步画成**相对第 6 步的退步**。
- ⇒ 正文第 164 行「[[term:throughput]] 的提升在这里来自重叠，而不是来自任何一处计算变快了」以及第 156 行「课件把这一步的价值讲得最清楚」，会让读者以为第 7 步是一次净提升。**按源的两组数字，只有「第 7 步相对第 4 步的串行版把时间压到 73%」成立；「第 7 步比它前一步快」不成立。** 建议正文明确写出比较基准（对第 4 步，不对第 6 步）。

## 我核不到的（诚实记录）

- **未缓存的 17 个演示页**（`mlsys-deck-tirx.html` 里出现、`_sources` 里没有）：`demo/tma_intro.html`、`demo/barrier_intro.html`、`demo/tirx_raw_cuda_ptx_tcgen05.html`、`demo/tirx_operator_dispatch.html`、`demo/step1_annotated.html`、`demo/step1_fullcode.html`、`demo/step4_load.html`、`demo/step4_store.html`、`demo/step4_fullcode.html`、`demo/pipeline_dynamic.html`、`demo/step7_annotated.html`、`demo/step9_motivation.html`、`demo/step9_roles.html`、`demo/step9_annotated.html`、`demo/mbarrier_arrive_timeline.html`、`demo/mbarrier_tma_timeline.html`、`demo/mbarrier_tcgen05_timeline.html`。**凡只可能落在这些页上的主张，我一律不下否定结论**，其中包括：
  - 「两条交替的时间线」（P1-6）—— `mbarrier_*_timeline*` 三页未缓存。
  - 「每一步都留了可运行的版本」（P1-3）—— `step*_fullcode` 系列未缓存；`summary_journey.html` 只标 4 步演示，这是我能拿到的上限证据。
  - 三个机制是否另有更详细的页面（`tirx_operator_dispatch.html` 未缓存）——正文的三个机制与 `however_cuda_cpp_painful.html` 逐条对得上，无冲突。
- **「127」的出处**（P1-4）：我检索了 `127`、`free`、`thread`（`evidence/**/*.html` 全树），命中的只有 `summary_journey.html` 的 `free 127 threads` 与 `sm_architecture.html`/`pipeline_arch.html` 的 `Only 1 thread dispatches`；课件**没有给 127 的推导**。所以我说「源里没有这条推导」，不说「127 是错的」。
- **幻灯片页码**：本讲源是 reveal.js 网页，页码不存在。我改用两套定位：① 主页面里的 `<h2>` 小节标题（如 `MBarrier: Data Structure & APIs`、`Warp Specialization: Overlap Everything`、`Distributed Shared Memory`、`The Optimization Journey`）；② 演示页自己的 `<h1>`/`<title>`。上面所有引用都是这两种标题 + 逐字原文。
- 我在源里**没有找到**与之对应的东西、因而既不能说对也不能说错的两句：① 第 124 行「三者的**共同目标**是让同一份程序在不同时候、不同人手里产生同一段机器码，这样性能才是可复现的」——`however_cuda_cpp_painful.html` 只说「deterministically dispatched to low-level PTX based on layout, slice and execution scope」，没有「共同目标 = 性能可复现」这句；② 第 174 行「同一块数据被两个 SM 的计算能力用上了」——源只写 `2× compute per SMEM tile`（`summary_journey.html`）与「cta_group=2 reads SMEM from both CTAs」（`step9_principle.html`），这句是合理转述，但「产出翻倍」的**计量口径**课件没写。

## 覆盖面

**配图（14 张 SV G，全部逐张通读：14/14）**：`blackwell-tirx-1.svg` … `-14.svg` 逐张读过 `<title>`、`<desc>` 与全部 `<text>`（`desc` 不渲染、只有通读才发现，这一条按方法 ⑦ 执行）。发现的问题：`-4.svg` 第 29 行「第 14 步」（P0-2）、`-4.svg` 与 `-10.svg` 的「每一步只改一件事」（P2-3）、`-12.svg` 的「各由一组 warp」（P2-4）、`-14.svg` 的「最后一步的目标 / 对齐 cuBLAS」与「每一步都留了可运行的版本」（P2-2、P1-3）。**数字类逐项回源结果**：`228`（`-2.svg`）= `sm_architecture.html`「228 KB per SM」✅；`127`（`-11.svg`）= `summary_journey.html`「free 127 threads」✅；`0.02` / `1322`（`-14.svg`）= `summary_journey.html`「From 0.02 to 1322 TFLOP/s」✅；`128` / `16` / `N 四档`（`-4.svg`）= `tcgen05_intro.html`（M 按钮 `disabled 128`、N 按钮 16/32/64/128、K 按钮 `disabled 16`）✅；`256 乘 256` / `两边各 128 行`（`-13.svg`）= `step9_principle.html`「128 rows in CTA-0's TMEM + 128 rows in CTA-1's TMEM → **256×256 total**」✅；**四字段**（`-6.svg`）= `mbarrier_mechanism.html` 四个 `obj-slot`（`phase` 0 or 1、`pending_count` arrivals left、`expected_count` total expected、`tx-count` bytes pending）+ 完成条件 `pending_count == 0 && tx-count <= 0` ✅；**三机制**（`-9.svg`）= `however_cuda_cpp_painful.html` 的 `.pillar` 1/2/3 ✅；**四组屏障**（`-12.svg`）= `step7_principle.html` 的 `tma2mma` / `mma2tma` / `mma2ld` / `ld2mma` 四张 `bcard` ✅（与正文第 162 行「数据就绪、缓冲可复用、累加完成、读走完成」一一对应）；**十步**（`-14.svg`）= `summary_journey.html` 的 10 项数组 ✅。

**源侧**：主页面 `mlsys-deck-tirx.html` 逐行读完（376 行）；已缓存的 10 个演示页**逐页逐行读完（10/10）**。**定向检索**（不是通读）的对象是未缓存的 17 页所在的一整棵 `evidence/**/*.html`，检索词与结果：`228`（命 3 处：`tirx/sm_architecture.html`、`tirx/pipeline_arch.html`、无关文件）、`1322|0.02`（命 `tirx/summary_journey.html`；另有 `however_cuda_cpp_painful.html` 的 CSS `0.02em` 属误命中）、`127`（命 `tirx/summary_journey.html`）、`eterministic|explicit layout|execution scope`（命 `tirx/however_cuda_cpp_painful.html`）、`Gluon|CuTe|CUTLASS|FlashAttention`（命 `tirx/why_cuda_ptx_native.html`）。**没搜到 ≠ 不存在**：以上否定性结论都限于「已缓存的 10 页 + 主页面的可见文字」这个范围。

**正文侧**：`content/15-blackwell-tirx/index.md` 208 行逐行读完；跨讲引用另读了 `13-ml-compiler-gemm/index.md`（检索 `TMA|张量内存|数据通路|SMEM` 后定位到第 102/108/164/170 行）、`14-llm-serving-1`（检索 `描述符`，0 命中）、`06-cuda-programming-1`（检索 `抽象距离`，命中确认第 6 讲原创此语）、`09-ml-parallelization-1`（检索 `通信|多机`，确认第 9 讲确有多机通信）、`16/19/20` 三讲（检索 `第 15 讲|Blackwell`，用于 ⑩）。
