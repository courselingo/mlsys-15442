# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 5 讲 Optimizing Linear Algebra（硬件加速）

- 核对人：**非作者**（`mit65840-reviewer`；按与 `fig-pruner` 的约定，本讲归我，L4 归它）
- 核对日期：2026-09-29
- 被核对版本：`content/05-optimizing-linear-algebra/index.md`
  归一化 SHA256 前16 = **357635CCA6F5E48C**
  （全 64 位 `357635CCA6F5E48CFED1924F8D7892C6F00F2106DFDC617B6CA71FAB403755A2`，16487 B）
  - 12 张配图（哈希入档，例：`-1 4B67FCA0D424B3B3`、`-10 C6118A4B87954324`、`-11 DC558FF67F95168D`）
- 源材料：

| # | 文件 | 用途 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-05-hardware-acceleration.pdf.faithful.txt`（1561 行，12222 B） | **主要依据**（`.faithful.txt`；按 Lead 规则**不用** `text-clean`） |
| 2 | 同上 PDF 的 `.embedded.txt` | **未使用**（mlsys 的 embedded 是字体二进制乱码，见第 2 讲记录里的证据） |

> 定位方式：**幻灯片标题 + 逐字原文**（faithful 有换页符，行号跨工具会差几行）。

---

## 结论

**P0（事实错误）：1 条 ｜ P1（易误解/依据不足）：1 条 ｜ P2（措辞）：2 条**

---

## P0 · 事实错误

### P0-1 行优先的地址公式写成了「i × **行数** + j」，源页与数学都是「i × **列数**（`A.shape[1]`）+ j」

- **正文 L50**：「课件给出的地址公式是：行优先时，第 i 行第 j 列的元素在 **`i × 行数 + j`** 的位置；列优先时两个下标调换。」
- **源（`Data layout and strides` 页）逐字**：
  ```
  A[i, j] => Adata[i * A.shape[1] + j]          ← Row major
  A[i, j] => Adata[j * A.shape[0] + i]          ← Column major
  A[i, j] => Adata[i * A.strides[0] + j * A.strides[1]]   ← Strides format
  ```
  ⇒ 行优先的步长是 **`A.shape[1]` = 列数**（一行的长度），不是行数；列优先才是 `A.shape[0]` = 行数。
- **为什么算 P0**：这是**读者会照着算地址的公式**，写成「行数」会直接算错（方阵时两个值相等，**非方阵时必错** —— 比如 3×5 的矩阵，
  行优先要乘以 5，按页面的写法会乘 3）。而且页面紧接着写「列优先时两个下标调换」——
  **那一半恰好是对的**（j × 行数 + i），所以这处错**读起来毫无破绽**，正是本项目最要防的那一类。
- **修在**：把「`i × 行数 + j`」改成「`i × 列数 + j`」，或直接照抄源页写「`i × A.shape[1] + j`」（更不容易再错）。
- **补充**：12 张配图里**没有**复现这个公式（我用 `行数|列数` 定向检索，配图 0 命中）⇒ **只需改正文一处**。

---

## P1 · 易误解或依据不足

### P1-1 延迟数字的「哪一级对应哪个数」以及三条倍数的归属，文本层核不到（可能差一级）

- **正文 L98**：「寄存器约 **0.5** 纳秒，L1 缓存约 **7** 纳秒，L2 缓存约 **200** 纳秒，再往外是 DRAM。课件额外标了两句对照：
  L1 比寄存器慢**十几倍**，L2 又比 L1 慢**二十几倍**，比寄存器则慢**两百倍以上**。」
  （同一组映射也出现在配图 `optimizing-linear-algebra-7.svg` 的可见文字与 `desc` 里 ✅ 图文一致。）
- **源（`Memory Hierarchy on Modern CPUs` 页，faithful 抽取的碎片，原样抄）**：
  ```
  0.5 ns
  7ns   14x L1 cache
  200
  ns
  20
  x L
  cache,
  200
  x L
  cache
  Latency
  Source: Latency numbers every programmer should know
  DRAM / L2 Cache / L1 Cache / Registers
  ```
- **我能确定的**：那一页确实有 `Registers / L1 Cache / L2 Cache / DRAM` 四行、有 `0.5 ns`、`7ns`、`200 ns` 三个数，
  有 `14x`、`20x`、`200x` 三个倍数标注，并且注明出处 `Latency numbers every programmer should know` ✅。
- **我核不到的**：**哪个数属于哪一级**、以及**三条倍数各自是比向哪一级**。
  碎片读起来像是「L2 = 14× L1」「再下一级 = 20× L2、200× L1」（这正是那组经典数字的标注方式），
  而页面把它写成了「L1 比寄存器 14 倍 / L2 比 L1 二十几倍 / L2 比寄存器两百倍以上」——
  两者**可能差一级**；但也不能排除页面就是对（页面自己写的那三个倍数是与它自己的三个数自洽的：7/0.5=14、200/7≈28.6、200/0.5=400）。
- **裁决**：**P1（依据不足）**，并**明确请求**：请拿该页的渲染图确认一次级别归属。
  **若原页确为「寄存器 0.5 / L1 7 / L2 200」且三条倍数就是相邻两级之比 ⇒ 本条可撤，降为无。**
  （**这一条我不判它是错的** —— 判错的证据不在文本层里。）

---

## P2 · 措辞

### P2-1 三处「示意」是页面补的，源页没有

| 位置 | 页面说 | 源里有的 |
| --- | --- | --- |
| L74 | 「**四个线程**各领四分之一的区间」 | `#pragma omp parallel for` + `Executes the computation on multiple threads`（**没写线程数**） |
| L62 | 「一个**几百兆**的矩阵做转置，零拷贝几乎是瞬间完成」 | `Transpose: swap the strides`（没有规模与耗时） |
| L154 | 「复用的收益是**乘性**的，额外循环的开销是**加性**的」 | 源只有 `Register cost : v1*v2 + v2*v3 + v1*v3` 与各条 cost 公式 |

⇒ 内容都成立、也都是合理的讲解；**建议**在溯源那句里把「示意性数字」也点一下（溯源目前已声明了「算力够但挨饿」等推论）。

### P2-2 「切出来的各段必须互不重叠」这条前提不在并行化那一页上

- **正文 L76**：「它同样带着前提，而且这个前提比对齐更要紧：切出来的各段必须互不重叠。」
- **源（`Parallelization` 页）全文**：代码 + `#pragma omp parallel for` + `Executes the computation on multiple threads` —— **没有这条前提**。
- 页面 L204 的溯源声明的是「并行化『各段不重叠』这条前提**在后续几讲的延续**」，**没有声明这条前提本身是我们补的**。
- ⇒ 建议：把它一并写进溯源（内容本身对，且是很关键的提醒，**不必删**）。

---

## 已核对通过（逐条附幻灯片标题 + 逐字引用）

| 正文 | 源 | 结果 |
| --- | --- | --- |
| L22 点题：参数更新写成 `w = w - lr * grad`；落到机器上要读三块数据、算一次乘加、写回 | `Running High Level Compute on Bare Metal` 页的计算图：`mul` / `learning_rate` / `sub` / `assign` / `w = w - lr * grad` | ✅ 逐字对应 |
| L26 课件把这一层标成 hardware kernel acceleration；先问「在你的程序上能做什么让它更快，无论 CUDA/x86 还是别的后端」 | 七层栈页：`Hardware Kernel Acceleration` + `This lecture`；`Discussion` 页：`What are the tricks you can do to make your program run faster on CUDA/x86/any backend ?` | ✅ 逐字对应 |
| L38 向量化例子：两段长度 **256** 的数组相加；标量循环 **256** 次；向量写法把**四个**数打包，循环 **64** 次 | 该页代码：`for (int i = 0; i < 64; ++i)` + `float4 a = load_float4(A + i*4)` + `float4 c = add_float4(a, b)`；`Adding two arrays of length 256` | ✅ **三个数字全对**（256 / float4 / 64） |
| L40 硬条件：三块内存都要按 **128 位对齐** | 同页：`Additional requirements: memory (A, B, C) needs to be aligned to 128 bits` | ✅ 逐字对应 |
| L50 行优先/列优先 + 步长格式的地址公式 | 见 **P0-1**（行优先那半错，列优先与步长格式两半对：`j * A.shape[0] + i`、`i * A.strides[0] + j * A.strides[1]`） | ⚠️ P0-1 |
| L52 步长格式更一般：行优先与列优先只是两组具体步长 | 同页三行公式并列呈现 | ✅ 对应 |
| L62 步长格式的三条好处：切片只改起点与形状、转置只交换两个步长、广播把某个步长设成 0；都是零拷贝 | `Stride Discussion` 页：`can perform transformation/slicing in zero copy way` / `Slice: change the begin offset and shape` / `Transpose: swap the strides` / `Broadcast: insert a stride equals [0]` | ✅ **三条逐字对应** |
| L64 三条代价：访问不再连续、向量化更难做、很多线性代数运算要先压实成连续数组 | 同页：`memory access becomes not continuous` / `Makes vectorization harder` / `Many linear algebra operations may require compact the array first` | ✅ **三条逐字对应** |
| L74 循环前加一行编译指令就分给多个线程；用的是 OpenMP 的 `#pragma omp parallel for` | `Parallelization` 页：`#pragma omp parallel for` + `Executes the computation on multiple threads` | ✅ 逐字对应（线程数见 P2-1） |
| L84 案例是矩阵乘 `C = A × B^T` | `Compute C = dot(A, B.T)` + `C[i][j] += A[i][k] * B[j][k]` | ✅ 逐字对应 |
| L88 朴素写法三层循环、`n³` 次乘加；课件马上把问题引向「数据从哪来」 | `Vanilla Matrix Multiplication` + `O(n^3)` + 三层循环代码 | ✅ 逐字对应 |
| L98 内存层级四级与延迟数字 | 见 **P1-1**（四行、0.5/7/200、14x/20x/200x、出处 `Latency numbers every programmer should know` 都核到；**级别归属核不到**） | ⚠️ P1-1 |
| L112 两笔开销：寄存器里 `n³` 次乘加；从 DRAM 载入也是 `n³` 量级再乘内存速度 | `Architecture Aware Analysis` 页：`register time cost: n^3` / `Load cost` … `* dramspeed * n^3` / `Register cost` | ✅ 逐字对应 |
| L124 寄存器分块：沿 i 切 v1、沿 j 切 v2、沿 k 切 v3 | `Register Tiled Matrix Multiplication` 页：`float A[n/v1][n/v3][v1][v3]` / `float B[n/v2][n/v3][v2][v3]` / `float C[n/v1][n/v2][v1][v2]` | ✅ 三个维度与命名逐字对应 |
| L126 「这一小块里的 a 被复用了 v2 次，b 被复用了 v1 次」 | 同页：`a get reused v2 times` / `b get reused v1 times` | ✅ **逐字对应** |
| L128 「寄存器里的乘加次数降到 **n³ 除以 v2**；载入次数也按同样比例下降」 | 同页标注：`register time cost: n^3/v2`（A 侧）与 `register time cost: n^3/v1`（B 侧） | ✅ **页面用的是课件自己的写法**（我一开始怀疑这句，回源后确认**页面对**） |
| L136/L140 缓存行分块：外层把 A 的一行与 B 的一行整段放进 L1，内层再套寄存器分块；两层叠起来才有效 | `Cache Line Aware Tiling` 页：`float a[b1][n] = A[…]`（标 `l1cache`）/ `b[b2][n] = B[j]` + `procedure, can apply register tiling here` | ✅ 逐字对应 |
| L148 复用规律：访问 A 用到 i 与 k、与 j 无关 ⇒ 把 j 方向切成 v 份就能复用 v 次 | `Common Reuse Patterns` 页：`Access of A is independent of j, tile the j dimension by v enables reuse of A for v times.` | ✅ **逐字对应** |
| L162 卷积：输出是四维张量，等于输入与权重在三个维度（通道维 + 卷积核两个空间维）上求和；输入/权重/输出各是四维张量 | 该页：`float Input[n][ci][h][w]; float Weight[co][ci][K][K]; float Output[n][co][h][w];` + `Output[b][co][y][x] = sum(Input[b][k][y+ry][x+rx] * Weight[co][k][ry][rx], axis=[k, ry, rx])` | ✅ **逐字对应**（含三个求和维度） |

**配图**：12 张做**定向检索**（关键词 `256`、`128`、`64 次`、`四个`、`行数`、`列数`、`0.5`、`7 纳秒`、`200`、`n³`、`v1`、`v2`、`不重叠`、`转置`），
命中并逐条比对的有：`-2`（256/64/128 位，✅ 与源一致）、`-5`（「前提是各段互不重叠」✅ 与正文一致）、
`-7`（0.5/7/200 的映射，⚠️ 与正文同一处 → P1-1）、`-8`（`n³` 与 `2 × 内存速度 × n³` ✅）、`-9`（`n³ / v2` ✅ 与课件标注一致）、`-11`（「输出是三个维度上的求和」✅）。
**`行数|列数` 在 12 张图里 0 命中** ⇒ P0-1 只需改正文。
**说明**：这是**定向检索**，不是逐张通读。

---

## 我核不到的（诚实记录）

1. **P1-1 的级别归属**（本讲唯一实质性缺口）：见上，范围 = 本讲 faithful 全文；检索词 = `0.5|7ns|200|14x|20|Latency|Registers|L1|L2|DRAM`。
2. **配图**：只做了上面那组关键词的定向检索，**没有逐张通读** 12 张图。
3. **第二份独立抽取**：mlsys 的 `.embedded.txt` 是乱码、`text-clean` 被 Lead 判为不可用 ⇒ 我只有 faithful 一份（这是本课所有讲次的共同限制）。

---

## 覆盖面（附录十二）

- **已验**：点题例子与计算图；hardware kernel acceleration 的定位与那句提问；向量化三个数字（256/float4/64）+ 128 位对齐；
  三种排法与三条地址公式（⇒ P0-1）；步长格式三条好处 + 三条代价（逐字）；OpenMP 写法；`C = dot(A,B.T)` 与 `O(n^3)`；
  内存层级四行与三个数 + 三条倍数（⇒ P1-1）；两笔开销公式；寄存器分块三维与 `a/b` 复用倍数 + `n^3/v2`；
  缓存行分块两层结构；复用规律的逐字表述；卷积四维张量与三处求和。
- **未验**：上面「我核不到的」3 条。

---

**核对人声明**：本记录只覆盖开头那个哈希的版本（`357635CCA6F5E48C`）。按附录五，对其它版本的结论不成立。
本记录只读正文、不修改任何 `content/` 文件；`status` 由 Lead 处理。
