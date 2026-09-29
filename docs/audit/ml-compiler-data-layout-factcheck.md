# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 12 讲 ML 编译器（上）：数据布局

- 核对人：**非作者**（独立核对；作者 `mlsys-author` 未参与，未提问、未改正文）
- 核对日期：2026-09-29
- 被核对版本：`content/12-ml-compiler-data-layout/index.md`
  归一化 SHA256 前16 = **9A902AF843E1EAC1**（20,098 B）
  - 14 张配图（哈希入档，例：`-4 3E3F36C8D25E488A`、`-6 D8E337128CE148D8`、`-12 9C7DE4C803D3782C`）
- 源材料：

| # | 文件 | 用途 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-deck-datalayout.html`（7,429 B，主页面） | 大纲、定义、记号页脚、具名轴、分布式轴、bank 背景、swizzle 三条 bullet 与收益句 |
| 2 | `evidence/datalayout/why_layout_simple.html`（3,785 B） | 逻辑下标 → 一维内存 |
| 3 | `evidence/datalayout/shape_stride_notation.html`（6,037 B） | `S[(4, 4) : (4, 1)]`、`addr(2, 3) = 11` |
| 4 | `evidence/datalayout/example_tiled_layout.html`（9,252 B） | 分块推导 `(4,2,2,4)/(16,4,8,1)`、`addr(2, 3) = 19` |
| 5 | `evidence/datalayout/example_replica_layout.html`（5,332 B） | `S[(2,4,8) : (1@gpuid_y, 8@m, 1@m)] + R[2 : 1@gpuid_x]` |
| 6 | `evidence/datalayout/bank_conflict.html`（5,396 B） | `bank = addr % 4`、两组对照与状态行 |
| 7 | `evidence/datalayout/thread_register.html`（**实为 `demo/thread_register.html`**，8,526 B） | `S[(8, 4, 2) : (4@laneid, 1@laneid, 1@reg)]`（分类问题见 P1-2） |
| 8 | `evidence/mlsys-webrepo-tree.txt` L117–139 | 该目录**实际有哪些** HTML（判断覆盖面用） |

> 定位方式：**小节标题 + 逐字原文**（网页课件的 HTML 全文，不是 faithful 文本层，所以本讲没有换页符/行号漂移问题；
> 但 `demo/` 下的交互页**未缓存**，见「我核不到的」）。
> 本讲**不用** `.embedded.txt`（字体二进制），也没有对应的 `text-clean`。

---

## 结论

**P0（事实错误）：1 条 ｜ P1（易误解/依据不足）：2 条 ｜ P2（措辞）：3 条**

---

## P0 · 事实错误

### P0-1 正文 L90 与图 6：「由**同一条线程内**的不同 lane 分担」——lane 是 warp 里的**不同线程**，不是一条线程内部的分段

- **正文 L90**：「`S[(8, 4, 2) : (4@laneid, 1@laneid, 1@reg)]` 里，前两段步长标着 `@laneid`，说明这部分由
  **同一条线程内的不同 lane** 分担；最后一段标着 `@reg`，说明它落在寄存器上。」
- **配图 `ml-compiler-data-layout-6.svg`**（可见 `<text>` 与 `desc` 两处都这么写）：
  - 可见文字（L23）：「标注为 @laneid 的部分 / **由同一条线程内的 lane 分担**」
  - `desc`（L4）：「…前两段步长标着 laneid，说明**由同一条线程内的不同 lane 承担**；最后一段标着 reg，落在寄存器上。」
- **源（`thread_register.html`）逐字**：
  ```
  <h1>Layout: S[(8, 4, 2) : (4@laneid, 1@laneid, 1@reg)]</h1>
  function threadLane(r, c) { return r * 4 + Math.floor(c / 2); }
  function threadReg(r, c) { return c % 2; }
  addr = row × 4@laneid + (col // 2) × 1@laneid + (col % 2) × 1@reg
  <table><tr><th></th><th>reg 0</th><th>reg 1</th></tr>
         <tr><th>lane ${lid}</th> …
  Each color pair = 1 thread (reg 0, reg 1)  |  laneid = threadIdx.x % 32
  ```
  - **同一个 lane 的「一行」里有 reg 0 与 reg 1 两格** ⇒ 寄存器那一级才是「一条 lane(线程)内部的再分段」；
    标 `@laneid` 的两级是**线程与线程之间**的分工。
  - 数值自洽核对：8×8 = 64 个元素；`threadLane ∈ [0, 31]` 共 **32** 个 lane；`threadReg ∈ {0, 1}` 共 **2** 个寄存器；
    **32 × 2 = 64** ✅。也就是**每个 lane（= 每个线程）持两个元素**，而不是「一个线程内部有两个 lane」。
  - 源里 `laneid = threadIdx.x % 32` 这一行是**定义级**的：lane 是 warp 内的线程编号。
- **本项目的既有口径也一致**：第 6 讲 L159「一个 warp 是 **32 个线程**，它们共用一条指令流」。
- **为什么算 P0（不是措辞）**：它把这一级的**方向讲反了** —— 数据在**不同线程之间**分配，源页却由页面写成在「一条线程内部」
  再分两段。这正是本项目最防的那一类：句子通顺、后面的结论（「谁算哪一块写成了布局的一部分」）也照旧成立，
  **不留任何困惑的痕迹**；而且错处在正文与配图（可见文字 + `desc`）**共三处**，只改正文会图文不一致。
- **建议修**：把「同一条线程内的不同 lane」改成「**同一个 warp 内不同的 lane（= 不同线程）**」；
  图 6 的 `<text>` 与 `<desc>` 同步改。`desc` 不渲染但读屏与搜索会碰到（方法⑦）。

---

## P1 · 易误解或依据不足

### P1-1 正文 L172 的「为什么是 8 行 8 列 / 128B」是一段机制推导，**已缓存的源里没有任何依据**，也没进溯源推论清单

- **正文 L170–172**：「为什么是 8 行 8 列这个形状。因为 fp16 的一个元素占 **2 字节**，8 列就是 **16 字节**，
  正好是一个 **128 字节**事务的**八分之一**；而 bank 的宽度也是按字节定的，于是 128B 这个模式恰好把这 8 行
  铺到 **8 个不同的 bank** 上。这个数字不是随便取的，它是存储宽度与元素大小共同决定的结果。」
- **源里有的**（主页面 `Real Example: SWIZZLE_128B` 那一页 + `Swizzle as a Memory Optimization` 页）：
  只有收益句本身 —— `Benefit: SWIZZLE_128B → conflict-free access to 8 rows and 8 columns at a time (fp16)`。
  「128」在全部已缓存源里共出现 **4 次**，全部是 `SWIZZLE_128B` 这个模式名（主页面 L163/165/167/176/178），
  **没有一处解释为什么是 8×8、也没有一处提到字节宽度**。
- **检索范围与检索词**：`evidence/datalayout/` 全 6 份 HTML + 主页面 `mlsys-deck-datalayout.html`，
  检索 `128|fp16|8 rows|8 columns|byte|bit|xor|XOR|swizzle`。命中只有：主页面上面那 5 行，
  以及 `thread_register.html` L44 一句注释 `// 32 laneid colors — same palette as swizzle bank colors`。
  **`byte` / `bit` / `xor` 在这 7 份里 0 命中。**
- **我不判它是错的**：这段推导要真出现在课件里，最可能的位置是 `slides/data_layout/demo/swizzle_128B.html`（18,862 B），
  而**这一份没有缓存，我拿不到**（见「我核不到的」）。所以本条的裁决是「依据不足」，不是「错」。
- **但有两件事需要处理**：
  1. 溯源 L211 的推论清单**没有列这一条**（清单列到「把位交换的廉价性归因于组合逻辑」为止）⇒ 按方法⑨的反面，
     页面自己的展开也要认下来；
  2. **计数体系叠了两次**（规则⑧）：本页前面讲 bank 用的是源里的 **4 个 bank** 教学模型
     （`bank = addr % 4`，两组对照 0/1/2/3 与 0/4/8/12），这里突然给出「**8 行铺到 8 个不同的 bank**」。
     两套 bank 数之间**没有一句换算或说明**（前者是源页的玩具模型，后者是 128B 模式下的真实分块）。
     建议加一句：「这里的一『段』是 16 字节，和前面 4 个 bank 的教学模型不是同一套计数」。

### P1-2 溯源 L209 的取证面与源目录对不上：被嵌入的 iframe 是 **11** 个，缓存清单里**缺 `img/why_layout_sharding.html`**，却把 `demo/thread_register.html` 算成「说明页面」

- **溯源 L209 原文**：「本讲的源是一份网页课件，正文之外的说明分散在若干被嵌入的交互页面里。…二是它嵌入的
  **六个说明页面**，分别是「为什么需要布局」「形状-步长记号」「分块布局的推导」「复制的布局」「内存 bank 冲突」
  「线程与寄存器布局」。两部分的原文都缓存为本地的 HTML 文件，逐字比对的是这两份 HTML 里的可见文字。」
- **源主页面 `mlsys-deck-datalayout.html` 里 `<iframe>` 共 11 个**：
  - `img/` 6 个：`why_layout_simple`、**`why_layout_sharding`**、`shape_stride_notation`、`example_tiled_layout`、
    `example_replica_layout`、`bank_conflict`
  - `demo/` 5 个：`tiled_layout`、`thread_register`、`tile_distributed`、`swizzle_8x8`、`swizzle_128B`
- **实际缓存到的 6 份**（`evidence/datalayout/`）：`bank_conflict`、`example_replica_layout`、`example_tiled_layout`、
  `shape_stride_notation`、`thread_register`、`why_layout_simple`
  ⇒ 与主页面的 6 个 `img/` 页相比 **少了 `why_layout_sharding.html`**（3,995 B 一份的说明页；
  仓库清单 `mlsys-webrepo-tree.txt` L133 记 5,451 B）；
  而多出来的 `thread_register.html`，在源仓库里属于 **`slides/data_layout/demo/thread_register.html`**（L121，8,526 B）——
  缓存件带 `click cell to see assignment` 的点击交互、`<body>` 上没有 `img/` 页才有的 `class="figure"`，
  是**交互演示**，不是 `img/` 下的说明页。
- **影响面**：本页**没有任何一句**依赖 `why_layout_sharding`（L36 的「或者不同的设备」出自主页面，已核到 ✅），
  所以这不是内容错误；但它让「六个说明页面」这个**计数与清单**同时不成立 ——
  被嵌入的页面是 11 个，「六个」既不是 11 也不是 `img/` 的那 6 个（清单把 `demo/thread_register` 顶替了 `img/why_layout_sharding`）。
  这正是规则⑧要查的「两套并存的计数体系，只说到了一套」。
- **建议修**：溯源改成「主页面 + 主页嵌入的 6 个 `img/` 说明页（逐字比对；其中 `why_layout_sharding` 未取到）+ 1 个
  `demo/` 交互页（`thread_register`）的 HTML 文本；其余 4 个 `demo/` 交互页未取、未复现」。

---

## P2 · 措辞

### P2-1 正文 L176–180「课件最后给了**三条建议**」的三条，与源页那三条 bullet 不是同一组

- **正文 L176/L180**：「课件最后给了三条建议。」→ 第一条「硬件施加的隐式重映射，打开即可」；
  第二条「把已经 swizzle 过的地址传进去，并在各个算子之间保持一致的模式」；第三条「不要自己算 swizzle」。
- **源（`Swizzle as a Memory Optimization` 页）原文分层**：
  ```
  **Swizzle is an implicit remapping the hardware applies — just enable it**      ← 粗体句
  - Pass pre-swizzled addresses and use a consistent swizzle mode (e.g. SWIZZLE_128B) across ops
  - Don't worry about swizzle yourself — let hardware handles it.
  - Benefit: SWIZZLE_128B → conflict-free access to 8 rows and 8 columns at a time (fp16)   ← 收益，不是建议
  ```
  ⇒ 源页 bullet 的第 **3** 条是**收益**；页面的「三条建议」= 粗体句 + 前两条 bullet，
  第 3 条 bullet 被挪到上一节当「收益」讲（L168，内容对 ✅）。内容都在，只是**「三条」这个数与源页那一组 bullet 对不上**。
- **建议**：写成「课件给了一句结论要照做（隐式重映射，打开即可）、两条 bullet 的做法、外加一条收益」，
  或直接照源页的粗体/项目符号分层写。

### P2-2 正文 L156/L160 的「位的交换」这个机制描述，在已缓存的源里 0 命中（溯源只声明了它的「廉价性」那条推论）

- **正文 L156**：「做法是在地址里做一些**位的交换**，把本来会撞到同一个 bank 的一批访问打散到不同 bank 上。」
  **L160**：「『位的交换』这个说法也解释了它为什么很快：交换几个位是纯组合逻辑，不需要查表，也不需要额外的存储。」
- **检索结果**：见 P1-1 那一次检索 —— `xor|XOR|byte|bit` 在已缓存的 7 份 HTML 里 **0 命中**；
  主页面只说 `Swizzle is fundamentally a way to enable efficient column access`，**没有说它怎么做**。
- ⇒ 「位的交换」这个机制大概出自未缓存的 `demo/swizzle_8x8.html` 或仓库里**未被主页面嵌入**的
  `img/xor_remap.html`（11,118 B，`mlsys-webrepo-tree.txt` L135），**我拿不到，不判对错**。
- 而溯源 L211 声明的是「把位交换的**廉价性**归因于组合逻辑」，**没有说明「位的交换」本身的出处** ⇒ 建议一并写清
  （这与 P1-2 是同一处取证面问题的两个症状）。

### P2-3 正文 L148 的「bank 数是 8」与最大公约数结论，是页面的延伸，溯源推论清单未列

- **正文 L148**：「还有一个细节值得留意：这四次访问的地址间隔是 4，正好等于 bank 数。…如果 **bank 数是 8** 而步长是 4，
  那么四次访问会落在两个 bank 上，冲突减半但仍然存在。也就是说，冲突的严重程度取决于步长与 bank 数的**最大公约数**。」
- **源只有 4 bank 的模型**：`bank = addr % 4` + 两组对照 + 状态行 `4/4 banks · 1 cycle · No conflict` /
  `1/4 banks · 4 cycles · 4-way conflict`。「8 bank」在已缓存源里 0 命中。
- **它本身自洽**（8 bank、步长 4 ⇒ 地址 0/4/8/12 落在 bank 0/4/0/4，2-way，4÷2 = 2 倍），
  按本项目先例（溯源有「课件未展开的推论属于 CourseLingo」一般条款时记 P2），建议把这条延伸补进溯源清单。

---

## 已核对通过（逐条附小节标题 + 逐字引用）

| 正文 | 源 | 结果 |
| --- | --- | --- |
| L24 大纲三条：分块与线程布局 / 分布式布局 / swizzle 布局 | 主页面 `Outline`：`Tiled & Thread Layout` / `Distributed Layout` / `Swizzle Layout` | ✅ 逐字 |
| L32 定义：把逻辑下标映射到数据所在的物理位置 | 主页面 `What is Data Layout`：`Mapping from logical indices to the phyiscal location of the data`（源页拼写即 `phyiscal`） | ✅ 逐字 |
| L36 第二种含义「或者不同的设备」 | 主页面同页：`or different devices...` | ✅ 逐字 |
| L44/L50 记号是 CuTe 的简化版、本讲采用行优先 | 主页面页脚：`This notation can be viewed as simplfied version of CuTe, with difference that we adopt row-major ordering.` | ✅ 逐字（含 `simplfied` 原拼写） |
| L48/L50 `S[(4, 4) : (4, 1)]`、`i × 4 + j × 1`、`A[2, 3]` 落在 11 | `shape_stride_notation.html`：`S[(4, 4) : (4, 1)]` / `addr(i, j) = i × 4 + j × 1` / `Example: addr(2, 3) = 2×4 + 3×1 = 11` | ✅ 三处数字全对 |
| L64–68 分块：形状 `(4, 2, 2, 4)`、步长 `(16, 4, 8, 1)`、下标重写 `(i//2, i%2, j//4, j%4)`、`A[2, 3]` 落在 19 | `example_tiled_layout.html`：`Layout: S[(4, 2, 2, 4) : (16, 4, 8, 1)]` / `Mapped indices (i//2, i%2, j//4, j%4)` / `Example: addr(2, 3) = 1×16 + 0×4 + 0×8 + 3×1 = 19` | ✅ 逐字 + 算式全对（含 `i//2=1, i%2=0` 这两个中间值） |
| L80 `S[(8, 16) : (16@m, 1@m)]`、`@m`、`@warpid`、`@tmemcol` | 主页面 `Named Axes in Strides` 页：`Row-major 8×16: S[(8, 16) : (16@m, 1@m)]` / `we use @m for normal meory` / `The @axis tag can also be other things like @warpid, or @tmemcol` | ✅ 逐字 |
| L90 记号本身 `S[(8, 4, 2) : (4@laneid, 1@laneid, 1@reg)]` | `thread_register.html` `h1` 与公式行 | ✅ 记号逐字对（**对它的解释见 P0-1**） |
| L104 两个轴名 `@gpuid_y` 与 `@gpuid_x` | 主页面小节标题 `Distributed Axes: @gpuid_y, @gpuid_x` | ✅ 逐字 |
| L114 `R[2 : 1@gpuid_x]` 是复制不是切开 | `example_replica_layout.html`：`R[2 : 1@gpuid_x]` / `R = replicated dimension` / `same data on both GPU_x=0 and GPU_x=1` | ✅ 逐字 |
| L118 8×8 矩阵放到 2×2 GPU 网格；`S[(2,4,8) : (1@gpuid_y, 8@m, 1@m)] + R[2 : 1@gpuid_x]` | 同页 `h1` + `GPU Mesh (2×2)` + `addr = (i//4) × 1@gpuid_y + (i%4) × 8@m + j × 1@m` | ✅ 逐字（含 `2×2`） |
| L130 不同 bank 可并行读；判断规则是地址对 bank 数取模 | `bank_conflict.html` 副标题：`bank = addr % 4 \| parallel reads only when accessing different banks` | ✅ 逐字 |
| L142/L144 两组对照：0、1、2、3 与 0、4、8、12 | 同页：`No Conflict, read [0, 1, 2, 3]` / `Conflict, read [0, 4, 8, 12]` | ✅ 逐字 |
| L144「同样是四次访问，花的时间可能差好几倍」 | 同页状态行：`4/4 banks · 1 cycle · No conflict` 与 `1/4 banks · 4 cycles · 4-way conflict` | ✅ 1 vs 4 cycles（「好几倍」成立） |
| L168（收益）fp16 下一次无冲突读 8 行 8 列 | 主页面：`Benefit: SWIZZLE_128B → conflict-free access to 8 rows and 8 columns at a time (fp16)` | ✅ 逐字 |
| L170「这个想法并不只属于 GPU 的共享内存」 | 主页面：`Swizzle is fundamentally a way to enable efficient column access — the idea is not specific to GPU shared memory!` | ✅ 逐字 |
| L38/L92/L96/L120 跨讲编号（第 5 / 6 / 8 / 9 / 11 讲） | 本仓库编号：05=optimizing-linear-algebra、06=cuda-programming-1（L159「一个 warp 是 32 个线程」）、08=transformer-attention（第 11 讲 L54 也把「重算换显存」记在第 8 讲）、09=ml-parallelization-1（`Data Parallelism and Zero Redundancy`=ZeRO）、11=memory-optimization（L144「完全分片的数据并行」、L150「权重分片」） | ✅ 五处归属与方向全部一致（按方法④逐条回源核过方向） |

**跨讲承诺（规则⑩）**：本讲对外的承诺只有 **L192「第 13 讲会看到这套记号怎么用在 GEMM 上」** 一条；
第 13 讲有专门一节 `## 这一讲与第 12 讲的关系`（L192–196）兑现 ✅。
反向检索**没有**发现别讲对本讲的承诺（检索词 `第 12 讲`、`下一讲`、`后面几讲`、`会讲`、`会看到`，
命中都是**回指**而非承诺）。

---

## 我核不到的（诚实记录）

1. **主页面的 5 个 `demo/` 交互页全部没拿到**（`tiled_layout`、`thread_register`、`tile_distributed`、
   `swizzle_8x8`、`swizzle_128B`，见 `mlsys-webrepo-tree.txt` L119–123）。
   ⇒ 因此下列**关于源的主张我核不到、不判对错**：
   - L54「课件的交互示例里，同一个矩阵可以按不同的步长摆成好几种样子」
   - L72「课件的交互示例允许**拖动**块大小，观察形状与步长怎么跟着变」
   - L142/L156/L160/L162 里关于 swizzle **怎么做**的部分（「位的交换」）⇒ 见 P2-2
   - L172 的「为什么是 8 行 8 列 / 128B」机制 ⇒ 见 P1-1
   检索词（对这 5 份的**替代检索面**：主页面 + 6 份已缓存 HTML）：`xor|XOR|swizzle|SWIZZLE|byte|bit|128|fp16|drag|slider`。
2. **`img/why_layout_sharding.html` 未缓存**（主页面 L55 引用的那张「or different devices」图）⇒
   我没有拿到它，**不能**说页面漏了它的内容，只能说我没核到。
   （`mlsys-webrepo-tree.txt` 里 `slides/data_layout/img/` 另有 5 份**未被主页面嵌入**的页：
   `shape_stride`、`tiled_layout`、`unified_view`、`why_layout`、`xor_remap` —— 也都没缓存；
   它们不在主页面的嵌入清单里，所以按「正文之外」的口径不算证据面，但 `xor_remap` 恰好是 P2-2 那个机制最可能的位置。）
3. **`demo/thread_register.html` 的交互行为**（点击单元格看 lane/reg 分配）我只能从它的源码读到「点击会发生什么」，
   **没有真的点**；本讲正文也没有依赖点击过程，只有 P0-1 依赖它的图例。
4. **没有第二份独立抽取可比**：本讲源是 HTML（不是 PDF），所以不存在 faithful/embedded 的交叉验证；
   我读的是缓存 HTML 原文，逐字比对的可信度高于 PDF 文本层，但**仍只有一份**。
5. 我**没有**去找课件的渲染截图（本讲没有 PDF 版；`slides/data_layout/` 只有网页版）。

---

## 覆盖面（附录十二）

- **正文**：14 张配图、212 行正文**全部读过**（正文逐行读完；配图见下）。
- **配图**：14 张 SVG **全部做了文本层通读**——用脚本把每张图的可见 `<text>` 与 `<title>/<desc>` 抽出来逐条比对
  （不是目视像素，也不是抽样）。命中并逐条比对：`-3`（`(4,4):(4,1)` / `11` / CuTe 页脚 ✅）、
  `-4`（`(4,2,2,4)` / `(16,4,8,1)` / `19` ✅）、`-5`（`@m` / `@warpid` / `@tmemcol` ✅）、
  **`-6`（「由同一条线程内的 lane 分担」⇒ 与正文同一处 → P0-1）**、`-7`（`@gpuid_x/@gpuid_y` ✅）、
  `-8`（`R[2 : 1@gpuid_x]` ✅）、`-9`/`-10`（bank 规则与两组对照 ✅）、`-11`（改变/不改变 ✅）、
  `-12`（`SWIZZLE_128B` 收益 8×8 ✅）、`-13`（三条建议 ✅ 与正文一致）、`-1`/`-2`/`-14`（无数字，与正文一致 ✅）。
  ⇒ **P0-1 需要同时改正文 L90 与图 6 两处文字**；其余各条**只需改正文**。
- **未验**：上面「我核不到的」1–5。

---

**核对人声明**：本记录只覆盖开头那个哈希的版本（`9A902AF843E1EAC1`）。对其它版本的结论不成立。
本记录只读正文、不修改任何 `content/` 文件；`status` 由 Lead 处理。
