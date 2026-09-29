# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 7 讲 GPU 架构与 CUDA 编程（下）

- 核对人：**非作者**（本讲任何一轮写作我都没有参与，也没有与作者 `mlsys-author` 讨论过本讲内容；
  我的角色就是本项目里的非作者事实核对者）
- 核对日期：2026-09-29
- 被核对版本：`content/07-cuda-programming-2/index.md`
  归一化 SHA256 前16 = **D0AB3D9DBC557BA0**
  （全 64 位 `D0AB3D9DBC557BA0B8B51C1A80734D00E85E19800C95ABCCDD0CEB167301E91A`，**16,528 B**；
  文件本身已是 LF，`\r\n` 归一化后长度与哈希都不变；最后写入 2026-09-29 10:22:48）
  - 12 张配图（`figures/cuda-programming-2-1.svg` … `-12.svg`）
- 源材料（本次实际依据的，逐个列出，并说明我怎么用它）：

| # | 文件 | 用途 / 说明 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-06-CUDA-programming.pdf`（5,526,037 B，**70 页**） | 权威源。原件含 788 个 NUL 与 917 个控制字符，我为阅读做了**去 NUL / 控制字符替换空格**的只读副本（未改源文件，副本在 `%TEMP%`）。**本讲与第 6 讲共用这一份课件** |
| 2 | 同目录 `.faithful.txt`（46,338 B，69 个 `===== PAGE =====` 分隔符 ⇒ 70 页文本块） | **主要依据**。按项目约定用 faithful，按「幻灯片标题 + 逐字原文 + 页码」定位，**行号不作坐标** |
| 3 | 同目录 `.embedded.txt`（15,547 B） | **未使用**。第 6 讲的核对记录已实测判定它是**字体二进制**（`OS/2`/`cmap`/`glyf` 一类） |
| 4 | `text-clean/*.txt` | **未使用**（按规则）。faithful 里有 `<03>`、`<07>`、`<08>`、`<0B>` 这类以控制码残留下来的字形，我用的是**同一份 PDF 的内嵌 ToUnicode CMap** 去解（见下面「文本层说明」），不是 `pdftext2.py`+`clean_text.py` 那条会留词内碎片的路径 |
| 5 | `_sources/mlsys-15442/evidence/mlsys-site-lectures.yml` | 核 `Week 4 (1)/(2) 共用 06-CUDA-programming.pdf`、本讲的**日期与周次**（`02/04 Wed`、`Week 4`） |
| 6 | `content/06-cuda-programming-1/index.md`、`content/05-optimizing-linear-algebra/index.md`、`glossary.toml` | 核本页的**跨讲指路**（L53/L63/L101/L113/L135）与 8 个 `[[term:…]]` |

> **页码约定**：下文一律用「**pN**」表示 **PDF 页码**（p1 = 第一页）。页脚编号与 PDF 页码的关系我逐页核过：
> **p1–p52 页脚 = PDF 页码**；**p53 是一页未编号的动画中间帧**（只有图形、无页脚）；**p54–p70 页脚 = PDF 页码 − 1**
> （p58 的页脚是 57、p70 的页脚是 69）。这与第 6 讲记录里的约定一致。
>
> **本讲的源范围 = p48–p70**（p48 是第二页 `Outline`，p49 起 `Strawman Implementation of Matmul`，
> p55 是第三页 `Outline`，p56 起 `Parallel Reduction`，p70 是 `Recap`）。

> **文本层说明（补一步，我在这里说明它是什么、不是什么）**：faithful 文本层对**普通正文**是完整的
> （`Each thread computes one element`、`Each thread computes a V x V submatrix`、`Multiple GPU threads access
> consecutive memory addresses`、`Problem: highly divergent warps`、`Cooperative/Coorperative Fetching` 等都能原样检索到）。
> 但 p50/p51/p52 的三个**访存量公式**在 faithful 里是以控制码残留的（`<03>t`、`<07>0<07>8`、`<C3><9B><08>z` 这种）。
> 我**没有**改用别的抽取器，而是按 `_sources/_audit/pdftext3.py` 自己的思路（PDF 内嵌 `ToUnicode` CMap）把
> `CambriaMath` 的 2 字节码解出来：`0x0374`→`2`、`0x0730`→斜体 `N`、`0x0738`→斜体 `V`、`0x072E`→斜体 `L`、
> `0x0B36`→上标 `²`、`0x0200`→`/`。于是 **strawman：`2*N` / `N²` / `2N³`**；
> **寄存器分块：`2NV` / `N²/V²` / `2N³/V`**；**共享内存分块：`2NL` / `N²/L²` / `2N³/L`**。
> 每一页的「每线程·每块值 × 个数 = 总量」三组数字**各自都自洽**（`2N·N²=2N³`、`2NV·N²/V²=2N³/V`、`2NL·N²/L²=2N³/L`），
> 这既是解码的自检，也是下面几条判断的依据。**残留说明**：总量式最前面那个字符（单字节 `0xDB`/`0xDC`）不在
> `CambriaMath` 的 CMap 里，我按上面三条等式把它读成 `2` 与上标 `3`（**这是反推，不是逐字识读**，见「我核不到的」第 1 条）。

---

## 结论

**P0（事实错误）：1 条 ｜ P1（易误解/依据不足）：5 条 ｜ P2（措辞）：5 条**

本讲的骨架——两个案例（矩阵乘 / 并行归约）、四条这条课反复出现的结论（寄存器分块、共享内存分块、协作加载、
内核分解绕开全局同步）、版本一与版本二的两处差别——我逐条回源核过，**方向、归属与公式都对得上**
（矩阵乘三个访存量公式、`tid % (2*s) == 0`、`index = 2*s*threadIdx.x`、`(j*nthreads+tid)/L` 与 `%L`、
`Expensive to build hardware...` / `Potential deadlock when # blocks > # multiprocessors * # resident blocks` /
`Code for all levels is the same` / `Kernel launch has very low hardware/software overhead` 全部逐字命中）。
**唯一一条 P0 是最后一节的收束计数**：课件那一页列的是**五个**要点，页面写成了四个。

---

## P0 · 事实错误

### P0-1 L151／L153／L157／L159／L179／L180／L181 与图 12：「课件把整份内容收成**四个**词」——课件最后一页列的是**五个**

- **正文 L151（小节标题）**：「## 课件收回来的**四个**要点」
- **正文 L153**：「这一讲最后，**课件把整份内容收成四个词**。」
- **正文 L157**：「相干 warp、合并访存、共享内存 bank 冲突、warp 级优化。前两个这一讲已经讲透；后两个只在收尾提了一句，属于留给读者的钩子。」
- **正文 L159**：「它们共同的地方是：**四个词**对应四种损失。」
- **正文 L179／L180／L181（溯源）**：「以及**课件收尾的四个优化要点**」「把**四个**要点归纳成「四种损失」」
- **图 12（`cuda-programming-2-12.svg`）**：`<title>`／图内可见文字＝`课件最后收回来的四个优化要点`；
  `<desc>`＝`相干 warp、合并访存、共享内存 bank 冲突、warp 级优化。四个词分别对应…`；
  图内末行＝`四个要点，对应四种损失`
- **源（p70，页脚 69，标题 `Recap`）逐字 + 缩进坐标**（x = 文本矩阵的水平位置）：

  | x | 逐字原文 |
  | --- | --- |
  | 73.241 | `Recap` |
  | 91.241 | `CUDA programming and GPU architecture` |
  | 91.241 | `GPU optimization techniques:` |
  | **127.27** | `Coherence warps` |
  | **127.27** | `Coalesced memory access` |
  | **127.27** | `Shared memory bank conflict` |
  | **127.27** | `Warp level optimizations` |
  | **127.27** | **`Tensor core`** |

- **判定**：`GPU optimization techniques:` 这一条下面**平级**有 **5** 项（`Tensor core` 的缩进 x = 127.27，
  与其余四项**完全相同**；上一级是 91.241，标题是 73.241 ⇒ 它**不是**更深一层的子项，也**不是**另一个顶层项）。
  页面的「四个词」是**对源内容的计数错误**，并且**整页（含溯源、含图 12）从头到尾没有出现过 `Tensor core` / 张量核心**。
- **为什么这条危险**：它读起来毫无破绽（method ① 里说的那种「讲得很顺」），而且这个「四」被页面用了四次
  （标题、正文、图、溯源），读者会把它当成课件的收束结构记下来。
- **建议**：改成「五个词」，补上 `Tensor core`（一句话即可，例如「还有一个是张量核心，它属于硬件单元，
  第 6 讲已经讲过它为什么出现」）；图 12 的 title/desc/末行与溯源同步改。
- **降级说明**：若 Lead 认为「四个词」指的是「四种**损失**」而不打算与课件的条目数对应，本条可降为 P1。
  但 L153 的原话是「**课件**把整份内容收成四个词」，主语是课件、宾语是课件的内容 ⇒ 我按就高原则记 P0，**请 Lead 裁决**。

---

## P1 · 易误解或依据不足

### P1-1 L41「代价**写在同一页上**」——p50 没有任何寄存器/占用率/常驻 warp 的文字

- **正文 L39–L41**：「做法是把每个线程负责的输出从「一个元素」改成「一个 V 乘 V 的小方阵」…**代价写在同一页上**：
  每个线程要占更多寄存器。寄存器是有限的，V 取大了会挤掉别的线程，反而让常驻的 warp 变少。」
- **源（p50，标题 `Optimization 1: Thread-Level Register Tiling`）该页的**全部**文字**（faithful 逐字 + CMap 解码）：
  ```
  Optimization 1: Thread-Level Register Tiling
  Compute
  Each thread computes a V x V submatrix
  __global__ void mm(float A[N][N], float B[N][N], float C[N][N]) { … float c[V][V] = {0}; float a[V], b[V]; … }
  Global memory access per thread: 2NV
  Number of threads: N²/V²
  Total global memory access: 2N³/V
  ```
  ⇒ **该页只有「每个线程算 V×V」与三个访存量公式**，没有寄存器数量、没有占用率、没有「常驻 warp」。
- **全篇检索**（faithful 去 NUL 后整篇匹配，不区分大小写）：`occupancy` **0**、`register` **1**（唯一那一处就是
  p50 的**标题** `Optimization 1: Thread-Level Register Tiling`）、`resident warp` **0**。
- **与页面自己的溯源冲突**：L181 明确写着「这类推论包括：…**把 V 的取值与常驻 warp 数联系起来**…属于 CourseLingo 的讲解」。
  ⇒ 页面一边声明这条联系是**我们的推论**，一边在 L41 说它**写在课件那一页上**。这不是漏声明，是**归属反了**。
- **建议**：把「代价写在同一页上」改成「代价要从代码里读（`float c[V][V]` 说明每个线程要 V² 个寄存器），
  课件这一页只给了三个访存量公式」，或直接加「（以下代价与占用率的关系是我们的展开）」。

### P1-2 L75／图 5 的三条用途里，「求最值」以及「均值与方差 / 指数和」的解释在源里没有依据

- **正文 L75**：「**课件说**它是很多机器学习系统算子的公共原语，**并举了几个**：归一化要先求均值与方差，
  softmax 要先求指数和，**还有一些地方要求最大值**。」
- **图 5（`cuda-programming-2-5.svg`）可见文字**：`归一化要用 / 先求均值与方差`、`softmax 要用 / 先求指数和`、
  **`求最值也要用 / 先扫一遍`**
- **源（p56，标题 `Parallel Reduction`）逐字**：
  ```
  Common and important primitive used by many MLSys operators:
  normalization, softmax, etc
  Tree-based approach to reduce elements within each thread block
  ```
- **全篇检索**（faithful 去 NUL 后整篇匹配，不区分大小写）：`variance` **0**、`mean` **0**、`average` **0**、
  `exponential` **0**、`maximum` **0**；`max` 共 **3** 处，**都与归约无关**——L2141（p29，第 6 讲范围）
  `Max warp execution contexts: 64`、L3817（p56）`softmax` 这个词内部、L5044（p66）
  `Maximize GPU memory usage`。
- **判定**：课件只点了 `normalization, softmax, etc` **两个名字**；
  「先求均值与方差」「先求指数和」是**我们的展开**，「**求最大值**」这一项在源里**完全找不到**。
  页面把三项都写成「课件…并举了几个」，读者去课件里找会找不到第三项。
- **建议**：改成「课件举了 `normalization` 与 `softmax`（后面还有 `etc`）；求均值/方差、求指数和是这两个
  操作各自的归约步骤，**求最值也是常见用法之一，不过课件这类里没写**」；图 5 的第三栏同步处理。

### P1-3 L61「**课件的理由是**：一个线程搬一整块要太久」——p54 只有代码，没有这句理由

- **正文 L61**：「**课件的理由是**：一个线程搬一整块要大久，做法是把这一块均分给块内所有线程，每个线程搬一份。
  分法通常是把这一块按元素编号摊平，用线程总下标去取模，这样每个线程拿到的量差不多。」
- **源（p54，标题 `Coorperative Fetching`；注意课件把 `Cooperative` 拼成了 `Coorperative`）该页的全部文字**：
  ```
  Coorperative Fetching
  sA[:, :] = A[k : k + S, yblock * L : yblock * L + L];
  int nthreads = blockDim.y * blockDim.x;
  int tid = threadIdx.y * blockDim.x + threadIdx.x;
  for(int j = 0; j < L * S / nthreads; ++j) {
    int y = (j * nthreads + tid) / L;
    int x = (j * nthreads + tid) % L;
    s[y, x] = A[k + y, yblock * L + x];
  }
  ```
  ⇒ **只有标题与代码**。整份课件检索 `slow`/`too long`/`one thread`+`load` 一类表述：本讲范围内
  **没有任何关于「为什么必须协作加载」的散文**（faithful 全文 `reason` 只出现在 p58 的 `Why?` 一节里，而那讲的是全局同步）。
- **判定**：这个理由是**合理的常识性推断**，但页面把它归给了课件（「课件的理由是」）。读者会以为课件写了这句话。
- **建议**：按页面 L181 的约定标成我们的推论，例如「课件只给了代码；不难看出**一个线程搬整块要很久**，
  所以这里把这一块均分给块内所有线程」。

### P1-4 L107「**课件给了两个版本**」与 L143「版本二的顺序寻址」——课件在这一段有三段不同的代码，页面从头到尾没有第三段

- **正文 L107**：「拆好之后，块内那一层怎么写，**课件给了两个版本**，逐版改进。」
- **正文 L119／L123**：「课件的**第二版**换了下标算法…让线程下标乘以两倍步长得到要访问的位置。」
- **正文 L143**：「**版本二的顺序寻址**让相邻线程访问相邻位置，既不发散，又是完全合并的。」
- **源（这一段实际有三段代码，各占一页）**：
  1. **p60／p61（`Version 1: Interleaved Addressing`）**逐字：`for(unsigned int s=1; s < blockDim.x; s *= 2) { if (tid % (2*s) == 0) { sdata[tid] += sdata[tid + s]; } __syncthreads(); }`
  2. **p64／p65（`Version 2: Strided Index and Non-divergent warp`）**逐字：`int index = 2*s*threadIdx.x; if (index < blockDim.x) { sdata[index] += sdata[index + s]; }`，
     页上注 `Replace divergent branch with strided index and non-divergent branch`
  3. **p69（页脚 68，标题 `Version 2: Sequential Addressing`）**逐字：`for(unsigned int s=blockDim.x/2; s > 0; s /= 2) { if (threadIdx.x < s) { sdata[threadIdx.x] += sdata[threadIdx.x + s]; } __syncthreads(); }`，
     页上注 `Replace strided index with reversed loop and threadId-based index`
- **问题所在**：第 3 段代码（消除合并访存那一步）在页面里**一次都没有出现**。
  L123 描述的跨步索引 `index = 2*s*threadIdx.x` 按 `2s` 跨步取址，**本身并不合并**；
  真正合并的是第 3 段的 `threadIdx.x` 直接当索引。页面把「消除发散」与「合并访存」都记在**同一个「版本二」**名下
  （课件自己在 p64 与 p69 也都写成 `Version 2`，所以这个混用**不是页面凭空造的**），
  读者会以为**一次改动同时解决了两件事**——这正是自测第 6 题要考的那件事，而页面没有给它可依据的材料。
- **建议**：把第 3 段代码点出来（一句即可，例如「最后一步是把跨步索引换成反转循环 + 直接用 `threadIdx.x` 取址，
  这样相邻线程才真正访问相邻地址」），并说明课件把 p64 与 p69 都标成了 `Version 2`。
  （L121 的图注「下面一条说**它还差最后一步**」已经在暗示这一步，但正文没有兑现。）

### P1-5 图 9（`cuda-programming-2-9.svg`）的 `<desc>` 说「让**连续的线程处理连续的位置**」——与 p65 的代码相反

- **图 9 `<desc>` 逐字**：「把下标算法换成「线程下标乘以两倍步长」，**让连续的线程处理连续的位置**；同一条判断对所有线程一致，warp 内不再有线程空等。」
- **源（p65）的代码**：`int index = 2*s*threadIdx.x;` ⇒ 相邻线程（`tid`、`tid+1`）取到的位置相差 **`2s`**，
  **不是连续位置**。
- **同一页簇的图 11（`cuda-programming-2-11.svg`）`<desc>`** 写的是「版本二的**顺序寻址**让相邻线程访问**相邻位置**」——**这句才对**，
  但它说的是**第三段代码**（p69 的 `threadIdx.x` 直接取址），不是图 9 要讲的跨步索引。
  ⇒ 两张图的 `<desc>` 口径冲突，且图 9 那句与它自己引的公式矛盾。
- **覆盖说明**：这句**只在 `<desc>` 里**，图 9 的可见文字是
  `版本二 / 线程下标乘两倍步长 / 效果 / 同一条判断对所有线程一致 / warp 内不再有线程空等 / 发散被消除了，但这还不是最后一步`，
  读者用眼睛看不到它；但 `<desc>` 是这个 SVG 随页面发布的 a11y 文本（`role="img"` + `aria-labelledby`）。
- **建议**：图 9 的 `<desc>` 改成「让**同一个 warp 内的线程进入同一分支**」（这是跨步索引真正做到的），
  把「连续的位置」留给图 11。
- **升降说明**：若 Lead 认为配图 `<desc>` 与正文同级，本条应升为 **P0**（它是对源公式的事实性反述）；我按「只在 desc 层」记 P1。

---

## P2 · 措辞

### P2-1 L61「用**线程总下标**去取模」与源的口径不同（L67 的写法才对）

源里取模的是**扁平的元素序号** `(j * nthreads + tid) % L`（`p54` 逐字），不是线程下标本身。
页面 L61 写「用线程总下标去取模」，两行之后的 L67 又写对了一次：
「先算出一个**扁平的元素序号**，再用行宽把序号拆回两个坐标…行号等于序号除以块宽，列号等于序号对块宽取余」。
⇒ 建议 L61 与 L67 统一到 L67 的口径。
（我核过一句话前提：只有当 `nthreads` 是 `L` 的整数倍时 `(j*nthreads+tid)%L == tid%L` 才成立，
而课件**没有**给出这个前提，所以不能默认两种写法等价。）

### P2-2 L123「要么全做，要么全不做」比课件的说法更强

正文 L123：「这样判断条件对所有线程是一致的：**要么全做，要么全不做**。同一个 warp 内的线程步调一致，发散就消除了。」
课件那边（p64 标题 `Version 2: Strided Index and Non-divergent warp`、p65 的 T/F 图）说的是 `non-divergent`：
p65 在 `s=1` 一行的取值是 **前 8 个 `T`、后 8 个 `F`**（`0..7` 为 T，`8..15` 为 F），`s=2` 是前 4 个 T，`s=4` 是前 2 个 T。
⇒ 判断条件并不是「对所有线程一致」，而是**与线程下标单调**（真值集中在前缀），
边界处仍然会分成两组。建议改成「判断条件变成单调的：下标小的先做、下标大的先不做，
同一个 warp 里不再交替真假」。

### P2-3 两处未标注的展开：把 [[term:latency]] 说成「事务数」，以及「多趟搬运」的副作用（按 why-ml-systems 的先例记 P2）

- **正文 L133**：「…一次**内存事务**就能服务整个 warp 的请求…**事务数**成倍增加，带宽被浪费掉。」
- **正文 L135**：「[[term:latency]] 在这里**不再是单个访问的时间**，而是**一批访问合起来占用的事务数**。」
- **正文 L103**：「这个解法还有一个副作用…每一趟都要把中间结果写回全局内存、下一趟再读出来…
  当级数很多、每级的数据又很小的时候，这些搬运本身就可能成为新的瓶颈。」
- **源**：`transaction` 全篇 **0 命中**；p66 只有 `Multiple GPU threads access consecutive memory addresses` /
  `Maximize GPU memory usage` 与图注 `coalesced access (optimal usage)` / `Non-coalesced access (suboptimal usage)`。
  p58／p59 也没有「中间结果要往返全局内存」的表述。
- **判定**：这些展开**内容本身是业界准确的常识**，问题只在出处；而且页面 L133 用的是「好处很直接」这种自陈口吻
  （不是「课件说」），L103 也是自陈。按 `why-ml-systems-factcheck.md` 里那次「P1 → P2」的自我更正尺度
  （L181 的「这类推论**包括**…」是**非穷尽**的一般条款），这里记 **P2**。
- **不过 L135 单独值得改**：把 [[term:latency]]（延迟）定义成「占用的事务数」，会让读者把**延迟**与**带宽**
  两个术语混起来——事务数衡量的是带宽利用率（也就是页面自己在 L145 说的「内存带宽的利用率」）。
  建议改成「这里要看的不是单个访问的延迟，而是一批访问合起来要占多少次内存事务，也就是带宽用得好不好」。

### P2-4 L179「两讲不重叠」在**页面层面**成立，但有两处已标注的交叉、以及一处方向相反的交叉，页面的溯源没声明

我按 Lead 的要求专门核了这件事，逐页核过页码：

- **覆盖范围确实不重叠** ✅：本讲取材落点的页码是 **p48–p70**（p48 第二页 `Outline`、p49 `Strawman`、
  p50 寄存器分块、p51 共享内存分块、p52 内存复用分析、p54 协作加载、p55 第三页 `Outline`、p56–p70 归约与收尾）；
  第 6 讲取材范围是 **p1–p47**（p44/p45/p46 是 GTX 980→H100 与 Tensor Cores，p47 是 Tensor Cores 那页）。
  两段**没有共同的页**。
- **但本讲确实引用了第 6 讲范围里的内容**（Lead 点名要查的那件事），一共两处，**两处都标了出处**：
  - L63：「搬完之后必须同步一次，**也就是第 6 讲讲的** `__syncthreads()`」⇒ 源是 **p25** `CUDA Synchronization Primitives`
    逐字 `__syncthreads(): wait for all threads in a block to arrive at this point`（属第 6 讲范围）✅
  - L113：「**这就是第 6 讲讲过的**发散执行」⇒ 源是 **p17** `Terminology` 逐字 `Divergent execution`（属第 6 讲范围）✅
  另一处 L101「**第 6 讲说**内核启动开销必须低，理由就在这里」⇒ 说的是第 6 讲的正文（第 6 讲 L151），
  而它的**依据页是 p58**（`Kernel launch has very low hardware/software overhead`），落在**本讲**范围内 ✅。
  ⇒ 这几处都是**明示的跨讲指路**，不是把第 6 讲的内容当新内容搬进来，没有上一轮别的课踩的那种坑。
- **还有一处方向相反的交叉**：本讲范围**最后那一页（p70 `Recap`）本身就在总结整份课件**——
  它同时列了 `CUDA programming and GPU architecture`（= 第 6 讲的两块）与 `Tensor core`（第 6 讲 p45/p46 的主题），
  以及 `GPU optimization techniques:`（= 本讲）。所以「不重叠」只是**取材划分**不重叠，
  课件的收尾页天然跨界。
- **第 6 讲的溯源已经声明了这处交叉**（`content/06-cuda-programming-1/index.md` L209：
  「两讲在「内核启动承担全局同步」这一处有少量交叉：本讲在讲块之间不能同步时引用到它，而它属于第 7 讲的并行归约那一段」），
  **本讲的溯源没有反向声明**。
- **建议**：在 L179 后面补一句（照第 6 讲的做法），例如「本讲在讲协作加载与发散时，各引了一处第 6 讲范围的内容
  （p25 的 `__syncthreads()`、p17 的 `Divergent execution`），都已在正文标出；课件最后一页的收尾同时总结了第 6 讲的两块。」
- **顺带（同一类，很小）**：L157 说「前两个这一讲已经讲透」——就「合并访存」而言成立（p66–p68 都在本讲范围）；
  但「**相干 warp**」这个说法（`Coherence warps`）整份课件**只出现在 p70 这一页**，
  `Coherence execution` / `Divergent execution` 两个术语在**第 6 讲 p17**。建议点明术语来源。

### P2-5 L179「课件的 outline 把内容分成四块：…GPU 架构…」——课件有**两页** outline，第二块的名字不一样

- 正文 L179：「课件的 outline 把内容分成四块：CUDA 编程抽象、**GPU 架构**、案例一矩阵乘、案例二并行归约。」
- 源：**p5**（第 6 讲范围）逐字 `Outline` / `CUDA Programming Abstractions` / **`GPU Architectures`** /
  `Cast Study 1: Matrix Multiplication in CUDA` / `Cast Study 2: Parallel Reduction in CUDA`；
  **p48**（本讲范围，就是标着 48 的那页）逐字 `Outline` / `CUDA Programming Abstractions` /
  **`CUDA Implementation on Modern GPUs`** / `Cast Study 1: …` / `Cast Study 2: …`。
  （两页都把 `Case` 拼成了 `Cast`，页面没有跟着抄错 ✅）
- ⇒ 页面这句对 **p5** 成立，但**紧挨本讲范围起点的那页 outline（p48）**用的是另一个名字。
  建议加一句「第二页 outline 把第二块写成 `CUDA Implementation on Modern GPUs`」，否则读者按 L14 去翻分节页会对不上。

---

## 已逐条回源、未发现问题的（抽样清单）

页码后为逐字原文（faithful 的 `<NN>` 控制码已按上文「文本层说明」解出）；行号为正文行号。

- p49（`Strawman Implementation of Matmul`）：`Each thread computes one element`、`Global memory access per thread: 2*N`、
  `Number of threads: N²`、`Total global memory access: 2N³`，代码 `result += A[x][k] * B[k][y];`、
  `int N = 1024; dim3 threadsPerBlock(32, 32, 1); dim3 numBlocks(N/32, N/32, 1);` ✅（L31／L33 的
  「每个线程负责输出矩阵的一个元素」「要读一整行与另一整个矩阵的一整列」= 每线程 2N 次 ✅；`2N·N²=2N³` 自洽 ✅）
- p50（`Optimization 1: Thread-Level Register Tiling`）：`Each thread computes a V x V submatrix`、
  `a[:] = A[xbase*V : xbase*V+V, k]; b[:] = B[k, ybase*V : ybase*V+V];`、`c[x][y] += a[x] * b[y];`、
  `Global memory access per thread: 2NV`、`Number of threads: N²/V²`、`Total global memory access: 2N³/V`
  ✅（L39「改成 V 乘 V 的小方阵」「一次读入服务 V 次计算」= 每个 `a[x]`／`b[y]` 在 V×V 内被用 V 次 ✅）
- p51（`Optimization 2: Block-Level Shared Memory Tiling`）：`A block computes a L x L submatrix` /
  `A thread computes a V x V submatrix and reuses the matrices in shared mem`、
  `__shared__ float sA[S][L], sB[S][L];`、`sA[:, :] = A[k : k + S, yblock * L : yblock * L + L];`
  ✅（L51「外层把 A 与 B 的一块搬进共享内存，块内所有线程共用这一份」✅；L53 的「一份数据从全局内存只读一次」
  **在「一个块的范围」内成立**：该块要用的 A 列条与 B 行条各 N×L 个元素，`2NL` 正是「各读一次」；
  跨块看每个元素会被 `N/L` 个块各读一次、总量 `2N³/L`——页面没写这层限定，但它的上下文（L51 起）讲的就是块内，我不判为错，
  只记在这里供作者判断）
- p52（`Analysis of Memory Reuse`）：`Global memory access per thread block: 2NL`、`Number of thread blocks: N²/L²`、
  `Total global memory access: 2N³/L`、`Shared memory access per thread: 2VN`、`Number of threads: N²/V²`、
  `Total shared memory access: 2N³/V` ✅（三组各自自洽；L53「在共享内存里被块内线程用很多次，再在寄存器里被复用 V 次」✅）
- p54（`Coorperative Fetching`）：`for(int j = 0; j < L * S / nthreads; ++j) { int y = (j*nthreads + tid)/L; int x = (j*nthreads + tid)%L; … }`
  ✅（L67「先算出一个扁平的元素序号，再用行宽把序号拆回两个坐标」「行号等于序号除以块宽，列号等于序号对块宽取余」**逐字对得上**）
- p56（`Parallel Reduction`）：`Common and important primitive used by many MLSys operators: normalization, softmax, etc`、
  `Tree-based approach to reduce elements within each thread block`
  ✅（L75 的「公共原语」与 L77 的「树形归约…每一步把规模减半」✅；**「求最大值」不在此列 ⇒ P1-2**）
- p57（`Challenges of Parallel Reduction in CUDA`）：`Task: for a large array of n elements, compute`、
  `Need to use multiple thread blocks (since a block is assigned to one SMM)`、`Each thread block reduces a portion of the array`、
  `How to communicate partial results between thread blocks?` ✅（L85 三句逐字对应）
- p58（`Problem: CUDA has no Global Synchronization`）：`Recall CUDA assumption: thread blocks can be executed in any order, cannot sync between them`、
  `Expensive to build hardware for GPUs with high processor count`、
  `Potential deadlock when # blocks > # multiprocessors * # resident blocks`、
  `Kernel launch serves a global synchronization`、`Kernel launch has very low hardware/software overhead`
  ✅（L85「kernel 里没有这种同步」、L87 两条理由、L97「每一次内核启动的边界…就是全局同步点」、
  L101「软硬件开销都很低」**全部逐字对应**；L87 把第二条读成「硬约束」是页面的归纳 ✅）
- p59（`Solution: Kernel Decomposition`）：`Avoid global synchronization by decompose computation into multiple kernel invocations`、
  `Code for all levels is the same` ✅（L97／L99 逐字对应）
- p60／p61（`Version 1: Interleaved Addressing`）：`for(unsigned int s=1; s < blockDim.x; s *= 2) { if (tid % (2*s) == 0) { sdata[tid] += sdata[tid + s]; } __syncthreads(); }`、
  `Why we need the two __syncthreads?` ✅（L111「每一轮的步长翻倍，参与的条件是线程下标能被两倍步长整除」**逐字对应**）
- p62／p63：`Problem: highly divergent warps` / `Version 1: Divergent Warps` ✅（L113「同一个 warp 里，一部分线程在做、
  另一部分在等」✅；p65 的 T/F 图逐个核过：`s=1` 为 `T F T F…`、`s=2` 为 `T F F F T F F F…`、`s=4` 为 `T F F F F F F F T F…`）
- p64／p65（`Version 2: Strided Index and Non-divergent warp`）：`int index = 2*s*threadIdx.x; if (index < blockDim.x) { sdata[index] += sdata[index + s]; }`、
  `Replace divergent branch with strided index and non-divergent branch`、
  T/F 图 `s=1` 前 8 个 T、`s=2` 前 4 个 T、`s=4` 前 2 个 T ✅（L119／L123 的做法描述 ✅；**「要么全做要么全不做」偏强 ⇒ P2-2**）
- p66（`Coalesced Memory Access`）：`Multiple GPU threads access consecutive memory addresses` / `Maximize GPU memory usage`，
  图注 `coalesced access (optimal usage)` / `Non-coalesced access (suboptimal usage)` ✅（L129 的「定义」**逐字对应**）
- p67／p68：`Version 1: Interleaved Addressing` + `Suboptimal memory accesses` ↔
  `Version 2: Sequential Addressing` + `Fully coalesced memory access` ✅（L143 逐字对应）
- p69（`Version 2: Sequential Addressing`）：`for(unsigned int s=blockDim.x/2; s > 0; s /= 2) { if (threadIdx.x < s) { sdata[threadIdx.x] += sdata[threadIdx.x + s]; } __syncthreads(); }`、
  `Replace strided index with reversed loop and threadId-based index` ✅（**这段代码页面没提 ⇒ P1-4**）
- p70（`Recap`）：五个优化要点（表格见 P0-1）✅／❌ 见 P0-1
- **cross-lecture**：L53「这和第 5 讲那条复用规律是同一件事」✅（第 5 讲 L146–L154 就是「复用的规律」，
  L150 用矩阵乘举例「访问 A 的时候用到了 i 和 k，与 j 无关…切 j 方向，同一份 A 复用 v 次」）；
  L135「第 5 讲的内存层级」✅（第 5 讲 L92 `## 内存层级：越靠近计算越快，也越小`，L98 引 `Latency numbers every programmer should know`）；
  L63／L113／L101 见 P2-4 ✅
- **8 个 `[[term:…]]` 全部在 `glossary.toml` 里有定义**（`kernel`／`ml framework`／`throughput`／`latency`／`compute`／
  `hardware accelerator`／`machine learning system`／`end-to-end`，**8/8 命中**；正文里 `[[term:kernel]]` 出现 3 次，
  所以引用总数是 9）✅
- **12 张配图与正文引用一一对应**（正文 12 条 `](figures/…)`，目录内 12 个文件，无「引用了不存在」也无「存在但未引用」）✅
- **本讲与第 6 讲共用课件、`Week 4 (2)`、`2026-02-04`** ✅（`mlsys-site-lectures.yml`：`02/04 Wed` / `Week 4: GPU Architecture and CUDA Programming (2)` /
  `slides: /slides/06-CUDA-programming.pdf`；`02/02 Mon` 是 `(1)`）；
  溯源 L178「课程仓库根 LICENSE，19,342 B」✅（`mlsys-webrepo-LICENSE.bin` 正好 19,342 B）

---

## 我核不到的（诚实记录）

> 按约定：**「我没找到」不等于「源里没有」。** 下面是我**没有**找到依据、或我**没有**条件核的部分。

1. **p50／p51／p52 三个总量公式最前面那个字形，我没有逐字解出来。**
   它是单字节 `0xDB`／`0xDC`，**不在 `CambriaMath` 的 `ToUnicode` CMap 里**（该 CMap 我能解析出
   `0x200`／`0x374`／`0x3c3`／`0x72e`／`0x730`／`0x738`／`0x745`／`0x878`／`0x87a`／`0x882`／`0xb35`／`0xb36`／…／`0x123e` 共 19 项）。
   我按**同一页三组数字互相约束**把它读成 `2` 与上标 `3`：
   `2N·N²=2N³`、`2NV·N²/V²=2N³/V`、`2NL·N²/L²=2N³/L` 三条等式**同时**成立（这是 method ⑤ 那种「同一页存在另一组约束」的用法）。
   ⇒ **这是反推，不是识读**；如果那两个字形其实不是 `2` 与 `3`，那么 p50/p51/p52 的「总量」三个数要整体重读。
   我**没有**去外部文献核这组数（按规则，只核「课件有没有这么说」）。
2. **p49–p54 那几张示意图里的标注我读不到**（faithful 只给文本对象，图片/矢量图形里的字不在文本层）。
   例如 p49 的 `A B C / N N N`、p51 的 `A B C / L L L L / N N S S`、p53 的 `E a c h t h r e a d c o m p u t e V x V`
   这些我还读得出，但**框线、箭头、灰底、块与块之间的对应关系不在我的范围**。
   ⇒ P0-1 里「`Tensor core` 与其余四项平级」这个结论**不是**靠图形得到的，是靠**文本矩阵的 x 坐标**
   （`GPU optimization techniques:` x=91.241，五项全部 x=127.27）与**相同的项目符号字形**（五项前面都带同一个字形）得到的。
3. **配图只核了文本层。** 12 张 SVG 我都读了全部 `<text>`／`<title>`／`<desc>` 节点（这一讲的 SVG **有** `<desc>`/`<title>`，
   与第 6 讲那 14 张不一样），但**几何（对齐、间距、箭头指向、颜色语义）没有逐条复核**。
   例如图 6 说「先开始的块在等后开始的块」这句我没有核它在画面上是否画成了「等待」的箭头。
4. **`text-clean/*.txt` 与 `.embedded.txt` 我都没有使用**，因此**没有**用第三份抽取产物交叉验证每一条
   （用的是 faithful + 同一份 PDF 的 CMap；`.clean.txt` 那条按规则排除）。
5. **检索范围与词（否定性结论一律附范围）**：
   - 正文 `content/07-cuda-programming-2/index.md` **L1–L181 全读**；源 faithful **p48–p70 共 23 页逐页读完**，
     并把 p1–p47 的**每页标题**也读了一遍用于核页码边界（不是逐字全读）。
   - P1-1：`occupancy` `register` `resident` `warp` `cycle` `latency` `cache`（全篇 faithful 匹配，命中数 0／1／0／多处／0／0／0）。
   - P1-2：`max` `maximum` `variance` `mean` `average` `exponential` `normalization` `softmax`
     （命中 3／0／0／0／0／0／1／1；并逐个核了 `max` 那 3 处的上下文）。
   - P1-3：`reason` `slow` `cooperative`/`coorperative` `load`（本讲范围内只有代码与标题）。
   - P1-4：逐页核了 `Version 1`／`Version 2` 出现的**全部 6 页**（p60、p61、p63、p65、p68、p69）的标题与代码。
   - P2-3：`transaction`（0 命中）。
   - P2-4：逐页核了 p1–p70 的**页脚号**与内容归属；并读了 `content/06-cuda-programming-1/index.md` 的 L204–L213（第 6 讲溯源）。
   - P0-1：读了 p70 的**文本矩阵 x 坐标**与项目符号字形（见第 2 条）。
6. **我换成别的写法找过的**（按「换了哪些写法」的要求）：
   `Tensor core` 我试过 `tensor core`／`Tensor Cores`／`张量核心`／`tensor`（faithful 里共 5 处：p44 的标题页、
   p45 的 `Tensor Cores`／`Matrix multiplication unit in SMM`、p46 的 `Tensor Cores`、p70 的 `Tensor core`）；
   「求最大值」我试过 `max`／`maximum`／`largest`／`reduction of`；
   「一个线程搬一整块要太久」我试过 `slow`／`one thread`／`cooperative`／`Coorperative`（课件把 `Cooperative` 拼成了 `Coorperative`，
   只按正确拼写搜会漏掉这一页）。

---

## 覆盖面

- **正文**：`content/07-cuda-programming-2/index.md` **L1–L181 全读**（含 front matter、6 道自测题、溯源）。
  **断言命中数**：8 个不同的 `[[term:…]]`（引用 9 次）、12 条 `](figures/…)` 引用、**14 个 `##` 小节标题**、
  正文出现「课件」**28 处**（我逐处核了它后面那句话在不在源里——P1-1／P1-2／P1-3 就是从这 28 处里挑出来的）、
  「第 6 讲」8 处、「第 5 讲」3 处、「四个」9 处。
- **源**：`06-CUDA-programming.pdf` 的 faithful **p48–p70 共 23 页逐页读完**；p1–p47 读了每页标题用于核边界；
  为解字形另读了同一份 PDF 的 `ToUnicode` CMap（**补充手段，已在上文「文本层说明」声明**）。
- **配图（两件事分开写，按 method ⑦）**：
  - **逐张通读：12 / 12 张**——每张 SVG 的**全部 `<text>` 文本节点 + `<title>` + `<desc>`** 都读了
    （这一讲的 SVG **有** `<desc>`/`<title>`，第 6 讲那 14 张当时是空的）。
  - **定向检索：12 / 12 张**——逐个查 `四个`／`四个要点`／`Tensor core`／`张量`／`事务`／`连续的线程`／`顺序寻址`／
    `版本二`／`bank` 的命中（例如 `连续的线程处理连续的位置` 只在图 9 的 `<desc>` 命中一次 ⇒ P1-5）。
  - **未做**：几何／箭头／位置／颜色的逐条复核（见「我核不到的」第 3 条）。
- **跨讲与元数据**：`mlsys-site-lectures.yml`（周次、日期、两份课件共用）、`content/06-cuda-programming-1/index.md`
  （第 6 讲的取材范围与它自己的交叉声明）、`content/05-optimizing-linear-algebra/index.md`
  （第 5 讲的「复用的规律」与「内存层级」两节）、`glossary.toml`（8/8 命中）。
- **哈希**：正文 SHA256 已钉在文首（前 16 = `D0AB3D9DBC557BA0`，16,528 B）。12 张配图我在这一轮**只做了文本层核对**，
  **没有**逐个钉配图哈希（若要钉，建议由 Lead 统一做，避免与本记录口径不一）。

---

**核对人声明**：本记录只覆盖基线前16 `D0AB3D9DBC557BA0`（16,528 B）。页面或配图再改动，结论不自动成立。
本记录**只读正文**，**不修改**任何 `content/` 下的文件，也不涉及 `status`（那是 Lead 的事）。
本讲与第 6 讲共用同一份课件，所以本记录的页码约定与 `cuda-programming-1-factcheck.md` 保持一致（pN = PDF 页码；
p1–p52 页脚 = PDF 页码、p53 未编号、p54–p70 页脚 = PDF 页码 − 1）。
