# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 6 讲 GPU 架构与 CUDA 编程（上）

- 核对人：**非作者**（`licence-prep`。**没有**参与本讲任何一轮写作，也没有与作者讨论过本讲内容；
  本人此前在本项目的角色是授权核实，与本讲写作无关）
- 核对日期：2026-09-29
- 被核对版本：`content/06-cuda-programming-1/index.md`
  归一化 SHA256 前16 = **073903298E0A0D1C**
  （全 64 位 `073903298E0A0D1CA0C61182946559E229BAE91F9440A6686DA5D904E464A271`，**19,234 B**；
  与 Lead 派单哈希一致 ✅。文件本身已是 LF，`\r\n` 归一化后长度与哈希都不变）
  - 14 张配图（前 16 位）：`-1 C181A017EB244A7A` · `-2 EE212DF2827779D3` · `-3 3F47155B76F9C1EC` ·
    `-4 553081443D434CF9` · `-5 DBEFD0433F4BB70A` · `-6 003A8AEF0A1D1408` · `-7 6D81A6A17CD5C314` ·
    `-8 7B72A16E8F628B05` · `-9 FD9E0787EE973572` · `-10 E32F8F8FC9E2F32B` · `-11 A77EB8F3B95A6C28` ·
    `-12 F0D2EF6F1B1935F6` · `-13 4BC0BC5FFE075D88` · `-14 365264AE110D9DD9`
- 源材料（本次实际依据的，逐个列出）：

| # | 文件 | 用途 / 说明 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-06-CUDA-programming.pdf`（5,526,037 B，**70 页**） | 权威源。页脚编号与 PDF 页码的关系我**逐页核过**：**p1–p52 一一对应**（p1→1、p21→21、p44→44、p48→48）；**p53 是一个未编号的动画中间帧**（只有图形、无页脚）；**p54 起页脚 = PDF 页码 − 1**（p54→53 … p70→69）。⇒ 下文一律用「pN」表示 **PDF 页码**，需要引页脚编号时单独注出 |
| 2 | 同目录 `.faithful.txt`（46,338 B） | **主要依据**（按项目约定用 faithful，按「幻灯片标题 + 逐字原文 + 页码」定位，行号不作坐标）。原件含 788 个 NUL 与 917 个控制字符，我为阅读做了**去 NUL / 控制字符替换空格**的只读副本（未改源文件，副本在 `%TEMP%`） |
| 3 | 同目录 `.embedded.txt`（15,547 B） | **实测是字体二进制**（`OS/2`/`cmap`/`glyf` 一类），课程文字 0 命中 ⇒ **未用于任何结论** |
| 4 | `_sources/mlsys-15442/evidence/mlsys-site-lectures.yml` | 核「Week 4 (1)/(2) 共用 `06-CUDA-programming.pdf`」与「后面讲显存优化」是否真有对应讲次 |
| 5 | `content/02-introduction-to-mlsys/index.md`、`content/05-optimizing-linear-algebra/index.md`、`glossary.toml` | 核本页的跨讲指路（L31／L67／L117／L139）与 8 个 `[[term:…]]` |

---

## 结论

**P0（事实错误）：0 条 ｜ P1（易误解/依据不足）：2 条 ｜ P2（措辞）：6 条**

---

## P0 · 事实错误

**0 条。**

（逐条回源范围内，没有找到与课件相冲突的断言。数字、定义、代码骨架、跨讲指路都对得上，见最后一节抽样清单。）

---

## P1 · 易误解或依据不足

### P1-1 L101／L105 与图 7 的**内存层级周期数**在课件里没有任何依据

- **正文 L101**：「三者的快慢差别很大，[[term:latency]] **从几个周期到几百个周期不等**。共享内存的位置居中……」
- **正文 L105**：「这里有一个量级上的直觉值得建立起来。**一次全局内存访问要等几百个周期，而一次共享内存访问只要几十个，寄存器更短。**」
- **图 7（`cuda-programming-1-7.svg`）文本层**：`内核能看到的三种内存，快慢差很多` / `每线程私有` / **`寄存器与本地内存`** / `每块共享` / `设备全局` / `三者的快慢差别很大` / **`全局内存最慢也最大`**
- **源（p21，标题 `CUDA Device Memory Model`）**该页正文**只有**（faithful 逐字）：
  ```
  Three distinct types of memory available to kernels
  Per-thread private memory (readable/writable by thread)
  Per-block shared memory (readable/writable by all threads in a block)
  Device global memory (readable/writable by all threads)
  Why shared memory?
  Enable cooperation across threads in a block
  ```
  ⇒ **既没有周期数，也没有「寄存器」「本地内存」，也没有快慢/大小的排序。**
- **全篇检索（对 `.faithful.txt` 去 NUL 后整篇匹配，不区分大小写）**：
  `cycle` **0**、`cycles` **0**、`latency` **0**、`nanosecond` **0**、` ns ` **0**、`hundred` **0**、`thousand` **0**、`dozen` **0**、`occupancy` **0**、`cache` **0**；
  `register` **1** 命中，且唯一那处在 **p50** `Optimization 1: Thread-Level Register Tiling` —— **属第 7 讲范围**。
- **与溯源冲突**：L210 第一句正面写着**「数字与定义以课件页面为准」**，而它紧接着列出的「这类推论包括…」清单里
  **没有**这两处周期数（清单只有：抽象距离与性能可推性、数据搬运成本与第 5 讲的关联、栅栏代价由最慢线程决定、
  内核启动开销必须低、块任意顺序读成调度不确定性、算力增长落在专用单元）。
- ⇒ 这两个数字**不是课件的话**，但正文把它们写成了对三种内存的客观描述，读者会当成课件内容。
- **建议**：要么去掉具体数字，只保留「差别很大」；要么明确标成我们的补充（例：「以下量级是我们的补充，课件此页未给数字」）。
- **降级说明**：若 Lead 认为 L210 的「包括」是非穷尽条款、足以覆盖一切未列出的补充，本条可降为 P2。
  但 L210 的**第一句**是正面声明（「数字以课件页面为准」），这两个数字**不在任何课件页上** ⇒ 我按就高原则记 P1，**请 Lead 裁决**。

### P1-2 「从 GTX 980 到 H100：什么没变，什么变了」漏掉了源页**同一页**列出的两组变化，会推出与源相反的印象

- **正文 L181（小节标题）**：「从 GTX 980 到 H100：什么没变，什么变了」
- **正文 L187**：「GTX 980 是 2014 年的卡：16 个 SMM，算力约 4.6 TFLOPs，每个 SMM 最多 64 个 warp、**96 KB 共享内存**。到 2022 年的 H100，课件列的对照是：**SMM 还是那个 SMM**，每个 SMM 的 warp 数还是 64，时钟频率只从 1064 涨到 1110 MHz。」
- **图 14 文本层**：「`没变的` / `SMM 还是那个 SMM`」「`变了的` / `算力靠专用单元推动`」
- **源（p44，逐字；抽取器把箭头 `->` 拆成 `-` 与 `>` 两个 run，下表按源页读法复原为 `→`）**：
  ```
  GTX 980 (2014) → H100 (2022)
  SMMs remain the same
  Clock speed: 1064 MHz → 1110 MHz
  Map warps per SMM: 64 → 64
  Threads per warp: 32 → 32
  Shared memory per SMM: 96 KB → 168 KB (A100) → 256 KB (H100)
  Streaming multiprocessors: 16 SMMs → 132 SMMs
  Peak performance 4.6 TFLOPs → 1000 TFLOPs (mainly because of tensor cores)
  ```
- **问题所在（有向/有范围的话）**：L187 把「**96 KB 共享内存**」放在 GTX 980 那一串参数里，紧接着说
  「SMM 还是那个 SMM」；读者最自然的读法是「H100 的 SMM 也是 96 KB、warp 数也一样」。
  而源页**同一份对照表**里，共享内存那一行是**变了的**（96 KB → 168 KB → 256 KB），
  SMM 总数也是**变了的**（16 → 132）。这两行在本讲正文与图 14 里**都没有出现**
  （检索：正文 `168` **0**、`256` **0**、`132` **0**；图里 `256` 的 2 次命中是 SVG 坐标，不是内存容量）。
- **注意**：源页自己的措辞确实是 `SMMs remain the same`，所以 L187 那句**不算错**；
  问题在于本节的标题与配图做的是**「什么没变／什么变了」的二分**，而二分的两份清单**各缺了一项**，
  于是「算力涨了 200 倍」被读成「只有张量核心是新增的」。
- **建议**：把源页那两行补进去（各一句即可）——「共享内存每个 SMM 96 KB → 168 KB(A100) → 256 KB(H100)」
  「SMM 总数 16 → 132」；或把标题改成「单元结构没变，单元内的资源与总量变了」。
  （源页把涨幅主因归给 tensor cores：`mainly because of tensor cores`，正文的因果方向与源一致，这一点不用改。）

---

## P2 · 措辞

1. **溯源 L208「九步动画」与源里可见的编号不一致**。原文：「课件里内核执行那一段原本是同一页幻灯片的**九步动画**。」
   源里这一段在 PDF 里展开为 **9 页（p32–p40）**，但页内的编号只到 **`Step 7`**（Step 1 p32、Step 2 p33、Step 3 p34 与 p35 重复、p36 是
   `THIRD BLOCK WON'T FIT DUE TO INSUFFICIENT SHARED STORAGE`、Step 4 p37、Step 5 p38、Step 6 p39、Step 7 p40）。
   ⇒ 若「九步」指 9 个动画帧/页，成立；按编号数会数到 7。建议写成「**九页动画（源里编号到第七步）**」，消除歧义。
2. **GTX 980 的时钟在源里有两种写法，正文只取了一种、未点明**。p43 逐字 `1.1 GHz clock`，p44 逐字 `Clock speed: 1064 MHz`。
   正文 L187 写「从 1064 涨到 1110 MHz」（与 p44 一致，取精确值是对的），但读者若去对 p43 会对不上。建议在溯源里记一句。
3. **L149「唯一的办法」是加重的说法**。源（p58）逐字是 `Solution: decompose into multiple kernels`，未称「唯一」。
   建议改为「课件给的解法是……」（另见第 5 条：这一页属第 7 讲范围）。
4. **L163「挑几个可执行的」丢掉了源里的确切上限**。源（p30）逐字 `Select up to four runnable warps from 64 resident on an SMM`
   与 `Select up to two runnable instructions per warp`；正文写「挑几个……一两条……」。
   ⇒ 「一两条」对得上，建议前半也写成「**最多四个**」，与后半一致。
5. **L207「两讲不重叠」在内容层面有一处小交叉**。L149（全局同步只能靠多次内核启动）与 L151（内核启动开销必须低）
   的依据页是 **p58 `Problem: CUDA has no Global Synchronization`**（含 `Kernel launch serves a global synchronization`
   与 `Kernel launch has very low hardware/software overhead`），而 **p55 起已是 `Cast Study 2: Parallel Reduction`，
   按 L207 的切分属第 7 讲范围**。⇒ 建议在溯源里点明「L149／L151 借用了第 7 讲范围的 p58 作旁证」，
   否则「两讲不重叠」这句会被读者当作绝对边界。
6. **内核执行那一段的示意参数与源页自己给的 96 KB 上限对不上，正文照录了源页说法**。
   p31／p29 给的参数是 `Each thread block allocate 130 * 4 = 520 bytes of shared memory` 与 `96 KB of shared memory`；
   p36 却写第三个块放不进去（`INSUFFICIENT SHARED STORAGE`）。按数学算 3 × 520 B ≈ 1.5 KB，离 96 KB 差三个数量级
   ⇒ 源页这里用的是**示意参数**（p36 括注里的数字是字形码，我没能解码，见「我核不到的」第 1 条）。
   正文 L175 写「课件在这一步标了一个具体情形：第三个块放不进去，因为共享内存不够」——**照录源页，不算错**，
   但建议补一句「课件此处用的是示意参数」。

---

## 已逐条回源、未发现问题的（抽样清单）

**关键句逐字对得上**（页码后为逐字原文，行号为正文行号）：

- p2／p3：`Conventional single instruction, single data processor` / `Modern single instruction, multiple data processor`；
  `Same instruction broadcast and executed in parallel on all ALUs` / `Add ALUs to increase compute capability` ✅（L23／L27）
- p5：`Outline` / `CUDA Programming Abstractions` / `GPU Architectures` / `Cast Study 1: Matrix Multiplication in CUDA` /
  `Cast Study 2: Parallel Reduction in CUDA` ✅（L207 的「四块」说法成立；**源页把 `Case` 拼成了 `Cast`**，正文没跟着抄错）
- p6：`Introduced in 2007 with NVIDIA Tesla architecture`；字形码 run 按 −3 位移解出 `"C-like" languages for programming on GPUs`
  与 `CUDA's abstractions closely match the capabilities performance characteristics of modern GPUs`；
  `Design goal: maintain low abstraction distance` ✅（L43／L41／L35；L35 的「课件原句」与图 2 的 `maintain low abstraction distance` 一致）
- p7：`Thread IDs are up to 3-dimensional (2D example below)`；代码 `const int Nx = 12; const int Ny = 6; dim3 threadsPerBlock(4, 3, 1);`
  与注释 `this call will trigger execution of 72 CUDA threads: 6 thread blocks of 12 threads each` ✅（L53 的「12 乘 6 / 4 乘 3」逐字对得上）
- p9：`gridDim: The dimensions of the grid` / `blockIdx: The block index within the grid` / `blockDim: The dimensions of a block` /
  `threadIdx: The thread index within a block` ✅（L51 四个变量的释义一字不差）
- p10：`Host` / `Device` / `__global__ denotes a CUDA kernel function runs on GPU` / `Call returns when all threads have terminated` ✅（L63）
- p11：`Separation of execution into host and device code is performed statically by the programmer`；
  字形码 run 解出 `Host` code = `serial execution on CPU`、`Device` code = `SIMD execution on GPU` ✅（L63）
- p12：`Number of SIMD Threads is Explicit in Program` / `Number of kernel invocations is not determined by size of data collection`
  ——**与 L75 的引述逐字一致**；代码 `Nx = 11; // not a multiple of threadsPerBlk.x`、`Ny = 5; // not a multiple of threadsPerBlk.y`、
  `if (i < Nx && j < Ny)` ✅（L75／L79）
- p15：`Mask (discard) Output of ALU` ✅（L87）；p16：`After Branch: Continue at Full Performance` ✅（L91）
- p17：`Coherence execution` / `Same instruction sequence applies to all elements` / `Necessary for efficient use of GPUs`；
  `Divergent execution` / `A lack of coherence execution` / `Should be minimized in CUDA programs` ✅（L89）
- p19：`Distinct host and device address spaces` / `Cannot access host memory from device` / `Cannot access device memory from host` ✅（L65）
- p20：`cudaMemcpy: Move Data Between Host and Device` ✅（L65「只能用显式的拷贝调用」；图 4 的 `数据只能靠 cudaMemcpy 在两边显式搬运`）
- p21：三类内存的「可读写范围」三行 ✅（L99；**周期数不在此页，见 P1-1**）
- p22：`output[i] = (input[i] + input[i+1] + input[i+2]) / 3.f;` ✅（L113「相邻三个输入的均值」）
- p23／p24：`each thread computes result for one element`；`__shared__ float support[THREADS_PER_BLK+2];` + `__syncthreads();` +
  `All threads cooperatively load block's support region from global into shared memory (total of 130 loads instead of 3 * 128 loads)` ✅（L113／L115）
- p25：`__syncthreads(): wait for all threads in a block to arrive at this point` / `Atomic operations` /
  `e.g., float atomicAdd(float* addr, float amount)` / `Implicit barrier across all threads at return of kernel` ✅（L125；L129「这一页没有展开同步的代价」也成立）
- p26：`Goal: run a CUDA program on various GPUs` / `High-end GPU (16 cores)` / `Mid-range GPU (6 cores)` ✅（L137）
- p28：`Major CUDA assumption: threadblocks can be executed in any order (no dependencies between threadblocks)` /
  `GPU maps threadblocks to cores using a dynamic scheduling policy that respects resource requirements` ✅（L147）
- p29：`Max warp execution contexts: 64 (up to 64 * 32 = 2K total CUDA threads)` / `96 KB of shared memory` ✅（L159）
- p30：`Warp: A group of 32 CUDA threads shared an instruction stream.` /
  `A convolve thread block is executed by 4 warps (4 warps x 32 threads / warp = 128 threads)` ✅（L159）；
  `Select up to four runnable warps…` / `Select up to two runnable instructions per warp`（**前者的「四」被略去，见 P2-4**）
- p31：`Each thread block execute 128 CUDA threads` / `Each thread block allocate 130 * 4 = 520 bytes of shared memory` /
  `Assume the host side launches 1000 thread blocks` / `Run the program on a two-SMM GPU` ✅（L173 的四个参数全部对得上）
- p33：`Step 2: scheduler maps block 0 to core 0 (reserves execution contexts for 128 threads and 520 bytes of shared memory)` ✅（L175）
- p38／p40：`Step 5: thread block 4 is scheduled on core 0 (mapped to execution contexts 0-127)` /
  `Step 7: thread block 5 is scheduled on core 0` ✅（L177「块结束后腾出的位置交给下一个块」）
- p41：`A warp is a CUDA implementation detail on NVIDIA GPUs` / `groups of 32 CUDA threads in a thread block are executed simultaneously using 32-wide SIMD execution` ✅（L159）
- p42：`Recall: An SMM on a NVIDIA GTX 980 (2014)` / `Map warp execution contexts: 64 (64 * 32 = 2048 total CUDA threads)` / `96 KB of shared memory` ✅（L159／L187）
- p43：`NVIDIA GTX 980 Contains 16 SMMs` / `16 x 4 warps x 32 threads / warp = 2048 SIMD mul-add ALUs = 4.6 TFLOPs` ✅（L187「16 个 SMM，算力约 4.6 TFLOPs」）
- p44：`SMMs remain the same` / `Clock speed: 1064 MHz → 1110 MHz` / `Map warps per SMM: 64 → 64` ✅（L187；**漏项见 P1-2**）
- p45／p46：`H100 Architecture with Tensor Cores` / `Tensor Cores` / `Matrix multiplication unit in SMM` ✅（L189「专门做矩阵乘加的电路」）
- p58：`Kernel launch serves a global synchronization` / `Kernel launch has very low hardware/software overhead` ✅（L149／L151 的内容依据；**范围问题见 P2-5**）

**跨讲指路四处都对**：

- L139「第 2 讲里那张『V100 快 30%、K80 慢 10%』的图」✅（第 2 讲 L136 图注与 L138 正文都有这两个数）
- L31／L67／L117「第 5 讲说的分块与复用……第 5 讲讲的是 CPU 上的缓存分块」✅（第 5 讲 L120–L142 是寄存器分块与缓存行分块，
  L98 引的正是 CPU 内存层级的 `Latency numbers every programmer should know`：L1 约 0.5 ns／L2 约 7 ns／DRAM）
- L67「后面讲显存优化」✅（课程排期里 Week 6 有 `Memory Optimizations: Tensor Rematerialization and Offload`）
- L14／L207「本讲与第 7 讲共用同一份课件」✅（`_data/lectures.yml` 里 Week 4 的 `(1)` 与 `(2)` 两行 slides 都指向 `/slides/06-CUDA-programming.pdf`）

**8 个 `[[term:…]]` 全部在 `glossary.toml` 里有定义**（`compute`／`latency`／`throughput`／`tensor-core`／`kernel`／
`hardware-accelerator`／`machine-learning-system`／`ml-framework`，8/8 命中）✅

**14 张配图与内容目录一一对应**：正文引用 14 张，目录内 14 张，无「引用了不存在」也无「存在但未引用」✅

---

## 我核不到的（诚实记录）

1. **p36 括注里的数字没能解码**。那一行是字形码 run：`\x0bWKLUG\x03EORFN…\x03VWRUDJH\x03\x16\x03[\x03\x18\x15\x13%\x03!\x03\x14\x11\x18.%\x0c`。
   按 −3 位移能解出 `THIRD BLOCK WON'T FIT DUE TO INSUFFICIENT SHARED STORAGE`，
   但**后面那个括注里的字符落在 0x0B–0x2E 区间，不是可打印 ASCII**，各字符的位移量不一致（数字用的可能是另一张字形表），
   我**没有解出来**。⇒ 我**不知道**源页这个括注写的是什么（很可能是 `3 × 520 B` 之类的算术），
   **因此不在这段乱码上对 P2-6 下结论**。
2. **图片对象里的文字读不到**。faithful 只给文本对象；p4／p8／p18／p22／p26／p45／p47／p60／p66／p67／p68 等页含大量
   图形/截屏，若**周期数、内存容量之类的数字是画在图里的**，我看不到。P1-1 的「周期数无源」结论仅限于**文本层**，
   但即便图里有数字，正文那两句也没有标出处 —— 结论不变，只是「源里完全没有」这句话要降级为「**文本层完全没有**」。
3. **配图只核了文本层**。这些 SVG **没有 `<desc>`/`<title>` 元素**（我用 `re.findall` 在 14 个文件里都查过，全为空），
   所以「逐张通读」读的是**全部 `<text>` 文本节点**；**图形、箭头、连线与几何位置没有逐条复核**
   （例如某个框画得对不对、箭头指向对不对）。这是我的覆盖面边界，不是「已确认无误」。
4. **页脚编号在 p53 之后整体差 1**（这不是错误，是记录坐标约定）：p1–p52 页脚 = PDF 页码；p53 是未编号的动画中间帧；
   **p54–p70 的页脚 = PDF 页码 − 1**（例：p58 的页脚是 57）。本记录里凡写「pN」都指 **PDF 页码**；
   正文若有人按页脚编号去找 P2-5 里那一页，会差 1。
5. **课件之外的通用事实**：CUDA 的真实内存延迟量级（几十/几百周期）我不去核外部文献 ⇒ 对 P1-1 **不判数字对不对**，
   只判「课件没说、正文却按课件内容写」。
6. **检索范围与词**（否定性结论一律附范围）：
   - 正文：`content/06-cuda-programming-1/index.md` **L1–L210 全部读完**；源：faithful **70 页逐页读完**。
   - P1-1：`cycle` `cycles` `latency` `nanosecond` ` ns ` `hundred` `thousand` `dozen` `register` `occupancy` `cache`
     （均在 faithful 去 NUL 后的全文上匹配，命中数见 P1-1）；另在**正文与 14 张 SVG** 上查 `周期` `纳秒` `延迟` `cycles` `latency`。
   - P1-2：`168` `256` `132` `1000 TFLOP` `8K` `TFLOPs`（正文与 14 张 SVG 双向查；图里 `256` 的 2 次是坐标）。
   - P2-1：逐页数 `Step N`（Step 1／2／3／3／—／4／5／6／7，共 9 页 p32–p40）。
   - 跨讲：第 2 讲 `V100|K80|30%|10%`、第 5 讲 `CPU|分块|缓存|cache`、排期 `Memory Optimization`、`glossary.toml` 的 `key =` 全表。

---

## 覆盖面

- **正文**：`content/06-cuda-programming-1/index.md` L1–L210 **全读**（含 front matter、6 道自测题、溯源）。**断言命中数**：
  8 个 `[[term:…]]`、14 条 `](figures/…)` 引用、正文 `周期` 3 处（= P1-1 的两句）。
- **源**：`06-CUDA-programming.pdf` **70 页逐页读完**（faithful；`.embedded.txt` 抽查后判定为字体二进制，未使用）。
- **配图（两件事分开写）**：
  - **逐张通读：14 / 14 张**——每张 SVG 的**全部 `<text>` 文本节点**都读了（这些 SVG 没有 `<desc>`/`<title>`）。
  - **定向检索：14 / 14 张**——对 `周期` `纳秒` `延迟` `168` `132` `256` `1000 TFLOP` `TFLOPs` `8K` 等词在 14 张图上逐个查命中。
  - **未做**：几何/箭头/位置的逐条复核（见「我核不到的」第 3 条）。
- **哈希**：正文与 14 张配图的 SHA256 已钉在文首（正文前16 = `073903298E0A0D1C`，与派单一致）。

---

**核对人声明**：本记录只覆盖基线前16 `073903298E0A0D1C`（19,234 B；14 张配图哈希已一并钉住）。
页面或配图再改动，结论不自动成立（`附录五`）。本记录**不修改**任何正文、配图或 `status`。
