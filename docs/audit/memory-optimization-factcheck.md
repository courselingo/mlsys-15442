# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 11 讲 显存优化

- 核对人：**非作者**（本讲任何一轮写作我都没有参与，也没有与作者 `mlsys-author` 讨论过本讲内容）
- 核对日期：2026-09-29
- 被核对版本：`content/11-memory-optimization/index.md`
  归一化 SHA256 前16 = **80FB91D946901DBA**
  （全 64 位 `80FB91D946901DBACD3E19DBC46EE1D0F3584AD8B8EE44062EACAF14D89D89C7`，**19,267 B**；
  文件本身已是 LF（`\r\n` 计数 0），归一化后长度与哈希都不变；最后写入 2026-09-29 10:55:18）
  - 14 张配图（`figures/memory-optimization-1.svg` … `-14.svg`）
- 源材料（本次实际依据的，逐个列出，并说明我怎么用它）：

| # | 文件 | 用途 / 说明 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-11-memory-optimization.pdf`（**443,184 B**） | 权威源。**取件校验（Lead 点名）**：体积 **443,184 B**、尾部 `f\r\n443000\r\n%%EOF`（`startxref` 指向 443,000 < 443,184）、大小**不是** 2 的整数次幂（**不是** `16384 = 2^14`）、对象层 `/Type /Page` **28**、`/MediaBox` **28**、`/Pages` 1、`/Count 28` ⇒ 确认拿到的是**复取后那一版**，不是截断件 |
| 2 | 同目录 `.faithful.txt`（**10,474 B**，9 个 NUL，27 个 `===== PAGE =====` ⇒ **28 个文本块**） | **主要依据**（按项目约定用 faithful）。只读副本在 `%TEMP%`，未改源文件。按「幻灯片标题 + 逐字原文 + 文本块序号」定位 |
| 3 | 同上，**页数与块数一致** | 28 个文本块 = 28 页（这一份没有前两讲那种「块数 ≠ 页数」的偏差），最后一块的标题是 `FSDP: Fully Sharded Data Parallel`，正是大纲的第三项 ⇒ **内容也是完整的 28 页那一版**（截断到 2^14 的那份只会有 6 页左右、不可能走到 FSDP） |
| 4 | 同目录 `.embedded.txt`、`text-clean/*.txt` | **一律未使用**（按规则） |
| 5 | `evidence/mlsys-site-lectures.yml`、`evidence/mlsys-course-schedule.html` | 核本讲的**周次、日期、讲者**，以及**课程表标题**（`Week 6: Memory Optimizations: Tensor Rematerialization and Offload`） |
| 6 | `content/02-introduction-to-mlsys/index.md`（跨讲承诺登记）、`content/08-transformer-attention/index.md`、`content/09-ml-parallelization-1/index.md`、`content/10-ml-parallelization-2/index.md`、`glossary.toml` | 核本页的**跨讲指路**（L54/L70/L82/L108/L164/L192）与 5 个不同的 `[[term:…]]` |
| 7 | `evidence/mlsys-webrepo-LICENSE.bin`（**正好 19,342 B**） | 核溯源 L212 的许可体积 |

> **文本层说明**：这一份的英文正文**几乎全部可读**（锚词 `We only need O(1) memory for computing the final output of a N layer deep network by cycling through two buffers`、
> `Only checkpoint colored nodes (step 0)`、`Recompute the missing intermediate nodes in small segments (step 1, 2)`、
> `Streaming aggregation`、`This is called reduce_scatter`、`Combine both we get Allreduce`、`Core idea is equivalent to ZeRO3`、
> `Shared memory: 64 KB per core`、`RTX3080 10GB`／`RTX3090 24GB`／`A100 40/80 GB`、`Some layers are more sensitive to dynamic range`、
> `Common issues: aggregation of a lot of entries` 等**全部原位命中**）。
> 少数公式仍是字形码（B7 的 `Training a 0 - layer neural network would require 1 0 memory`、B9 的 `/AIKNU ?KOP L 1 0 - E 1 : - ;`）——
> 我按上下文读作 `O(N)`／`O(N + N²/k)` 这一类，**没有把字形码当成逐字引用**。

---

## 结论

**P0（事实错误）：1 条 ｜ P1（易误解/依据不足）：3 条 ｜ P2（措辞）：5 条**

Lead 点名要逐个回源的四件事，**四件都在，且都能找到逐字依据**：
**激活检查点与重算** ✅（B8 的 `Only checkpoint colored nodes (step 0)` / `Recompute the missing intermediate nodes in small segments (step 1, 2)`，B9 标题 `Sublinear Memory Cost`）；
**混合精度 float16 vs bfloat16** ✅（B11 标题 `16bit Floating Points`、`float16`／`bfloat16`／`More fraction bits`／`Less easy to overflow`，B12 的 `linear f16`／`softmax f32`）；
**AllReduce 拆成 reduce_scatter + allgather** ✅（B21 `Reduce Scatter Abstraction`、B26 `Allgather abstraction`、B27 逐字 `Combine both we get Allreduce`）；
**FSDP 等价于 ZeRO3** ✅（B28 逐字 `Core idea is equivalent to ZeRO3`）。
**唯一一条 P0 出在配图的可见文字上**（正文与它自己的 `desc` 都是对的，是图里那句话写反了）——这正是「只有逐张通读才会碰到」的那一类。

---

## P0 · 事实错误

### P0-1 配图 `-10.svg` 的可见文字把三者关系写反了：它说「前两个合起来，就是最后一个」（＝allreduce + reduce_scatter = allgather）

- **配图 `figures/memory-optimization-10.svg` 的 `<text>` 节点（我按坐标核过视觉顺序）**：
  ```
  x=381.0 y=48.0   三个通信抽象，一个比一个基础
  x=381.0 y=95.9   三个抽象的接口
  x=345.0 y=170.9  allreduce：每个设备都拿到完整归约结果        <- 第 1 行
  x=345.0 y=251.9  reduce_scatter：每个设备拿到其中一片的归约结果  <- 第 2 行
  x=345.0 y=332.9  allgather：每个设备把自己那一片发给所有人      <- 第 3 行
  x=345.0 y=410.7  前两个合起来，就是最后一个                   <- ✗ 这一句
  x=345.0 y=428.7  所以通信原语可以拆开单独用
  ```
  ⇒ 按渲染顺序，「前两个」＝ allreduce ＋ reduce_scatter，「最后一个」＝ allgather；**这是错的**。
  正确的合成关系是 **reduce_scatter ＋ allgather ＝ allreduce**（也就是它自己的第 1 行）。
- **源（B27，标题 `Overall Relations`）逐字**：图上先画 `Allgather`，再画 `Reduce Scatter`，最后一行写的是 **`Combine both we get Allreduce`**。
- **本页其他地方都对**：正文 L140 逐字「**后两个合起来就是第一个**」✅；同一张 SVG 的 `desc` 逐字也是「**后两个合起来就是第一个**」✅。
  也就是说：**同一张图里，不渲染的那句（desc）是对的，渲染给读者看的那句错的**——说明文件第 ⑦ 条提醒的正是这个方向。
- 建议：把这句改成「后两个合起来，就是第一个」（或「reduce_scatter + allgather = allreduce」），顺手把标题那半句「一个比一个基础」也改成中性说法
  （三个原语里 allreduce 是最高层抽象，`reduce_scatter`/`allgather` 更底层，「一个比一个基础」容易被读成新到旧的排序）。

---

## P1 · 易误解或依据不足

### P1-1 〔⑩ 跨讲承诺〕第 2 讲登记的「第 11 讲：展开重算与**换出**」——**换出这一半没有被兑现，也没有在溯源里说明**

- **第 2 讲页面（`content/02-introduction-to-mlsys/index.md`）溯源的承诺登记，逐字**：
  「本页作出的跨讲承诺在此登记，供后续讲次产出时回核。第 4 讲：…。**第 11 讲：展开显存的两种省法（重算与换出）**。…」
- **课程表（两个取件）对 02/18 那一讲的标题，逐字**：
  `mlsys-course-schedule.html`：`02/18 Wed` → `Week 6: Memory Optimizations: Tensor Rematerialization and Offload`，slides 指向 `/slides/11-memory-optimization.pdf`；
  `mlsys-site-lectures.yml` L100-107 同样写 `Week 6: <strong>Memory Optimizations: Tensor Rematerialization and Offload</strong>`。
- **本讲课件（deck 11）的实际内容**：B2/B3/B9/B13 四个大纲页逐字都是
  `Activation Checkpointing and Rematerialization` / `Mixed Precision` / `Fully Sharded Data Parallelism`；
  我把整份 28 页文本过了一遍关键词：`offload` **0**、`swap` **0**、`cpu` **0**、`host` **0**、`pinned` **0**。
  ⇒ **课件本身没有「换出」**（`rematerialization` 4 次、`checkpoint` 8 次、`shard` 10 次都在）。
- **本页**：三个手段写的是「激活检查点与重算 / 混合精度 / 完全分片的数据并行」（L24，与大纲一致 ✅），
  全页没有「换出 / offload / 卸载到主机内存」；溯源 L213 也没有说明「课程表标题里的 Offload 这一讲没讲」。
- ⇒ 这是**跨讲承诺只兑现了一半**（重算 ✅、换出 ❌）。本页跟着课件写是对的，
  但「答应过的事没做」应当**显式记录**（至少溯源加一句：课程表标题为 `Tensor Rematerialization and Offload`，本讲课件未覆盖 Offload）。
  这一条不是本页能独自修的，建议 Lead 决定是补内容、还是改第 2 讲那条承诺 / 由后续讲次承接。

### P1-2 L24 与配图 `-1.svg` 的「前两块省的是训练时的中间值」与 L176「混合精度省的是**所有数值**的位宽」自相矛盾

- **正文 L24 逐字**：「课件把内容分成三块：激活检查点与重算、混合精度、完全分片的数据并行。**前两块省的是训练时的中间值**，第三块省的是模型本身的副本。」
  **配图 `-1.svg` 可见文字逐字**：「前两块省的是中间值，第三块省的是模型副本」。
- **正文 L176 逐字**（同一页里）：「检查点与重算省的是中间激活值；**混合精度省的是所有数值的位宽，也就是把每一份都变小**；完全分片省的是每块卡上的模型副本。」
- **源（B5，标题 `Sources of memory consumption`）逐字**：
  ```
  Sources of memory consumption
    Model weights
    Optimizer states
    Intermediate activation values
  ```
  ⇒ 显存的三份底账里，混合精度动的是**每一份**（权重、优化器状态、激活值都降位宽），
  「中间值」只描述得了检查点那一半。L176 是对的，L24/图 `-1` 那句话会让读者以为混合精度只作用于激活值。
- 建议：L24 与图 `-1` 改成「第一块省的是中间值，第二块把每一份数值都变小，第三块省的是模型副本」。

### P1-3 L96「这是它比另外两个手段更受欢迎的原因」——没有源依据，也没有登记为推论

- **正文 L96 逐字**：「[[term:latency]] 与显存在这里是同一个方向上的收益，降精度既省容量也省带宽，**这是它比另外两个手段更受欢迎的原因**。」
- **源**：B11/B12（混合精度那两页）只给了 `More fraction bits`／`Less easy to overflow`／`linear f16`／`softmax f32`／
  `Some layers are more sensitive to dynamic range`／`Common issues: aggregation of a lot of entries`／
  `Mixed precision: different input/output/accumulation types`，**没有任何「更受欢迎」的比较**；
  课件也没有把三个手段互相排名（四个大纲页都是并列三条）。
- 溯源 L214 的推论清单里**没有**这一条（登记的是「把混合精度的搭配解释成线性层不敏感而 softmax 敏感」）。
- ⇒ 「A 比 B 更受欢迎」是方法 ④ 点名的那类**比较判断**：要么补依据、要么改成「它同时省容量与带宽」这种可核的说法，要么登记为我们的判断。

---

## P2 · 措辞

| # | 位置 | 正文 | 源 / 说明 |
| --- | --- | --- | --- |
| P2-1 | L44 | 「每核 64 KB 共享内存，**注册器**更小」 | 「注册器」应为「**寄存器**」（register）；源 B4 逐字 `Shared memory: 64 KB per core` 与 `Registers`。同处源还有一行 `A100 40/80 GB`，本页省略（写的是「这个量级」，不算错，补上更完整） |
| P2-2 | L8 / L13 / L210 | 「Week 6 — Memory Optimizations（**Tianqi Chen、Zhihao Jia 主讲，2026-02-17**）」 | 课件 B1 标题页逐字 `Memory Optimizations / Spring 2026 / Tianqi Chen / and Zhihao Jia / … / 2/17/2026` ⇒ 日期与两个名字都取自课件的**课程署名行** ✅；但课程表写的是 `02/18 Wed`、lecturer 只有 `Tianqi Chen`。**周次 `Week 6` 对** ✅（02/17 与 02/18 都在第 6 周）。三讲里第 9 讲用的是课程表的写法、这一讲用的是课件署名行的写法，建议统一并注明来源 |
| P2-3 | L154 | 「于是加卡真的能装下更大的模型。**这也是为什么它被称为「零冗余」**」 | 「零冗余」是 **ZeRO** 的名字（第 9 讲溯源逐字：「全称 Zero Redundancy Optimizer」）；源 B28 只说 `Core idea is equivalent to ZeRO3`，**没有**说 FSDP 叫零冗余。FSDP 的名字逐字是 `FSDP: Fully Sharded Data Parallel` |
| P2-4 | 溯源 L214 | 推论清单 | 下列几处是本页的判断但**没有登记**：按小段重算比按点重算划算（L56）、k 的两个极端（k=1 不留、k=N 只留入口，L68）、把相邻若干层合并成一次 allgather（L168）、调参次序「先定精度、再定检查点密度、最后定分片策略」（L184） |
| P2-5 | L94 | 「课件在这一页点了一句：有些层对精度更敏感」 | 源 B12 其实是**两条**：`Some layers are more sensitive to dynamic range` 与 **`Common issues: aggregation of a lot of entries`**（后者才是 softmax 留在 f32 的课件理由）；本页把原因写成「指数运算 + 归一化」（已登记为推论）⇒ 建议把源那两条也逐字引出，读者才知道课件原来点的是「动态范围」与「大量元素求和」 |

---

## 跨讲承诺（说明文件第 ⑩ 条）

- **本讲作出的、带讲次编号的承诺：0 条**（L26「前面几讲反复出现的那句」、L194「四讲连起来」都不给编号）。
- **本讲引用的别的讲次（逐条核）**：
  | 位置 | 指路 | 核对结果 |
  | --- | --- | --- |
  | L54 | 「和第 **8 讲** FlashAttention 用重算换显存是同一个套路」 | ✅ 第 8 讲页面有小节标题逐字「**重算：用一次计算换一大块显存**」与小节正文「技术二是重算：前向不保存那个注意力矩阵，反向的时候再算一遍」（其溯源也把这两件事归到「用计算换搬运」） |
  | L70 | 「和第 **5 讲**的块大小、第 **8 讲**的分块尺寸、第 **10 讲**的微批次数都是同一类」 | ✅ 三个编号都对得上（第 10 讲讲微批次是事实） |
  | L82 | 「第 **8 讲**提到的那个 **65504** 的上界，就是 float16 的问题」 | ✅ 第 8 讲页面 L118 逐字提到 `16 位浮点能表示的最大值只有 65504` |
  | L108 / L164 | 「这正是**上一讲**那个「每个工人约 2M」的另一种数法」／「这正是**上一讲** ZeRO 第三阶段的那笔账」 | ✅ 上一讲＝第 9 讲：其页面 L114/L207 逐字有「每个工人约 2M」，其课件 `Overall communication: 2 * M * N`（环形）与 `ZeRO Stage 3: Partitioning Parameters` 都在；方向与对象都对 |
  | L192 | 「第 **5** 讲…第 **8** 讲…第 **9** 讲…这一讲把剩下三种省显存的手段补齐」 | ✅ 对得上（第 5 讲片上存储、第 8 讲注意力平方项、第 9 讲 ZeRO） |
- **别人对本讲的承诺**：第 2 讲登记过「第 11 讲：展开显存的两种省法（重算与换出）」⇒ **只兑现了一半**，见 P1-1。

## 配图（覆盖面：逐张通读 14 张，定向检索 0 张）

- **逐张通读 14 张**：把每张 SVG 的 `<text>` 节点**连坐标一起**读出来（坐标用来定渲染顺序），并读了不渲染的 `desc`。
  **本轮唯一一条 P0 就是这样抓到的**（`-10.svg` 的可见文字与它自己的 desc 相反）。
- **有没有两张「可用文字几乎相同」**：**没有**。两两 Jaccard 最高 **0.188**（`-1.svg` 与 `-13.svg` 都在讲三种手段的分工，但用词不同），
  其余 ≤0.143 ⇒ 不构成「同一骨架复用」问题。
- 版面：14 张的 `<rect>` y 分带实测 **6 种**（与第 9 讲那份实测到的种类数相同；其中 **9 张**共用 `(10,70,140,230)` 这一组 y 分带，
  但它们的 rect 数与文字都不同，所以不是同一张图）。
- 配图里需要注意的地方：只有 `-10.svg`（P0-1）与 `-1.svg`（P1-2）；其余 12 张逐句对回源都对得上，例如
  `-2.svg` 的「两块缓冲区循环使用／显存与层数无关／N 层网络要 O(N) 的显存」= B6/B7 逐字；
  `-3.svg` 的「课件的说法是着色节点」「从最近的检查点按小段重算」= B8 逐字 `Only checkpoint colored nodes (step 0)` / `Recompute the missing intermediate nodes in small segments (step 1, 2)`；
  `-11.svg` 的「等价于 ZeRO 的第三阶段」= B28 逐字 `Core idea is equivalent to ZeRO3`。

## 我核不到的（诚实记录）

1. **float16／bfloat16 的位数**（L84「float16 有 10 位小数位与 5 位阶码，bfloat16 有 7 位小数位与 8 位阶码」）：
   源 B11 的文字层只有 `float16`、`bfloat16`、`More fraction bits`、`Less easy to overflow`、`source: wikipedia`，**位数在图里**。
   这两个数本身符合 IEEE 754（binary16 = 1+5+10，bfloat16 = 1+8+7），**我不判错**，但也**没有**在本讲文本层里核到它们；
   溯源 L214 也没把它们登记为推论/外部常识。建议溯源补一句「位数取自该页仓位图（课件标注 source: wikipedia）」。
2. **B9 的公式**（`Sublinear Memory Cost` 那一页）：`Forward computation`／`Gradient per segment with re-computation`／`Checkpoint cost`／`Re-computation cost` 都能读，
   但两个式子（`/AIKNU ?KOP L 1 0 - E 1 : - ;`）仍是字形码，`+0x1D` 位移也解不出（该位移在本讲只对 B30 那种子集……本讲没有那种子集）。
   ⇒ 本页 L64/L72 只说「与 k 有关」「把重算算进反向开销」，**没有替课件补公式**，这一点与源不冲突 ✅；具体式子我核不到，不判对错。
3. **B7 的 `O(N)`**：文字层是 `Training a 0 - layer neural network would require 1 0 memory`（`N` 与 `O(N)` 都是字形码），
   我按上下文与页面标题 `Activation Memory Cost for Training` 读作 `O(N)`；**这是读法推断，不是逐字命中**。
4. **源 B21 自己有一处笔误**：标题是 `Reduce Scatter Abstraction`，但示例代码写的是 `b = comm.allreduce(a, op=sum)`（`assert b == [2,2]`／`[4,5]`）。
   **本页没有复述这段示例**，所以不受影响；若以后要引这一页，注意这是课件的笔误，别照抄。
5. **B4（`Recap: GPU memory hierarchy`）与 B5（`Sources of memory consumption`）这两页没有出现在溯源 L213 的取材范围里**
   （L213 只写了「此外，课件还用一页回顾了显存层级」）——B5 那三项 `Model weights / Optimizer states / Intermediate activation values`
   其实是本讲「省的是什么」的底账，也与 P1-2 直接相关。这不算内容错误，但**取材范围清单漏了一页**。
6. 我**没有**对这份 PDF 做对象级/坐标级的另一次抽取：本环境没有 pdftotext / mutool / qpdf / ghostscript（我逐个查过），
   也没有 pypdf / PyPDF2 / pdfminer。上面对齐关系（例如 B27 图里 `Allgather` 先于 `Reduce Scatter`）是按文本块顺序读的；
   结论依赖的是那句逐字 `Combine both we get Allreduce`，与顺序无关。

## 已逐条回源、未发现问题的（供作者放心，不重复计 P）

- 推理 O(1)：B6 逐字 `We only need O(1) memory for computing the final output of a N layer deep network by cycling through two buffers`；L36 ✅（「循环使用两块缓冲区」= `cycling through two buffers`）。
- 训练 O(N)（读法见上）：B7 逐字 `Because the need to keep intermediate value around (checkpoint) for the gradient steps.` + `We will use the following simplified view to combine gradient and forward computation`；L38/L42 ✅。
- 检查点两步：B8 逐字 `Step 0:` / `Step 1:` / `Step 2:` + `Only checkpoint colored nodes (step 0)` + `Recompute the missing intermediate nodes in small segments (step 1, 2)`；L52/L56 ✅（「着色的节点」= `colored nodes` ✅）。
- k 层一个检查点：B9 逐字 `For a 0 layer neural network, if we checkpoint every - layers`（`N`/`k` 为字形）+ `Forward computation` + `Gradient per segment with re-computation` + `Checkpoint cost` + `Re-computation cost`；L64/L66/L72 ✅。
- 两个格式：B11 标题 `16bit Floating Points`、`float16`、`bfloat16`、`More fraction bits`、`Less easy to overflow`；L80 ✅（「float16 小数位更多、更容易溢出；bfloat16 阶码更长、不容易溢出、精度低一些」与那两条标签一致）。
- 混合精度的搭配：B12 逐字 `linear f16`、`softmax f32`、`Some layers are more sensitive to dynamic range`、`Common issues: aggregation of a lot of entries`、`Mixed precision: different input/output/accumulation types`；L90/L94 ✅。
- AllReduce 的两个半场：B15 逐字 `Form a logical ring between nodes` + `Streaming aggregation`；B20 逐字 `Each node have correctly reduced result of one segment!` + `This is called reduce_scatter`；L116/L118/L120 ✅。
- 复杂度那一问：B25 逐字 `Question: What is Time Complexity of Ring based Reduction`；L130 ✅（本页给出的 2M 已登记为推论，并与第 9 讲课件逐字 `each worker sends 2*M parameters (independent to the number of workers)` 一致 ✅）。
- 三个接口：B14 `result = allreduce(float buffer[size])`、B21 `result = reduce_scatter(float buffer[size])`、B26 `result = allgather(float buffer[size])`；L138 ✅；
  B27 逐字 `Combine both we get Allreduce`；L140 ✅（**正文对**，错的是配图，见 P0-1）；L142 的「四个元素」= B27 图的 `A/B/C/D` ✅。
- FSDP：B28 逐字 `FSDP: Fully Sharded Data Parallel` / `Core idea is equivalent to ZeRO3` / `Weights shard on different GPUs` / `Allgather` / `Full weight replicated in each GPU` / `Forward (local)` / `Drop full weight after forward` / `Backward (local)` / `Gradients shards on different GPUs` / `Reduce Scatter` / `Local W gradient on each data slice`；L150/L162/L164 ✅
  （「前向 allgather 出完整权重、用完立刻丢、反向再凑一次、梯度用 reduce_scatter 归约回去」逐句都能对上）。
- 显存层级：B4 逐字 `Shared memory: 64 KB per core`、`GPU memory(Global memory):` `RTX3080 10GB`、`RTX3090 24GB`、`A100 40/80 GB`；L44 ✅（除 P2-1 的「注册器」与省略的 A100）。
- 溯源 L212 的许可体积：`mlsys-webrepo-LICENSE.bin` 正好 **19,342 B** ✅。
- 5 个 `[[term:…]]`（`compute`、`throughput`、`tensor-core`、`latency`、`hardware-accelerator`、`data-parallelism`、`ml-framework`、`kernel`、`machine-learning-system`）在 `glossary.toml` 里都有对应条目 ✅。
