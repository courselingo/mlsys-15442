# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 2 讲 Introduction to Machine Learning Systems

- 核对人：**非作者**（复用 mit-6.5840 七讲记录的核对者身份 `mit65840-reviewer`）
- 核对日期：2026-09-29
- 被核对版本：`content/02-introduction-to-mlsys/index.md`
  归一化 SHA256 前16 = **2B3EBEC0F45D454B**
  （全 64 位 `2B3EBEC0F45D454BFF5BE7B3A298BB4470517D082B1432829669A39BD99D059C`，19538 B）
- 源材料（逐个列出，并说明我怎么用它）：

| # | 文件 | 用途 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-02-introduction-to-MLSys.pdf.faithful.txt`（2802 行，18682 B） | **主要依据**：Week 1 第 2 次课课件（`https://mlsyscourse.org/slides/02-introduction-to-MLSys.pdf`）的 **faithful 文本层** |
| 2 | `_sources/mlsys-15442/evidence/mlsys-site-lectures.yml`（5545 B） | 核**讲次编号**（页面上有「第 4 讲 / 第 9、10 讲 / 第 11 讲 / 第 19 讲」四处指路） |
| 3 | `_sources/mlsys-15442/evidence/mlsys-slide-02-introduction-to-MLSys.pdf.embedded.txt` | 只用来做一次反证，见下（**它对这个 PDF 是坏的**） |

> **文本层说明（这一段本身就是给 Lead 的证据）**
> 按规则本讲只用 `.faithful.txt`。我顺手试了一下同一 PDF 的**原始内嵌抽取**（`.embedded.txt`），
> 结果是 **二进制乱码**——`Select-String` 在它里面匹配到的是 `OS/2`、`cmap`、`cvt`、`fpgm`、`glyf`、`head`、`hhea`、`hmtx`、`loca`、`maxp`、`name`、`post`、`prep`
> 这一串**字体表名与字形数据**（即把 PDF 里的嵌入字体当成文本流抓出来了）。
> ⇒ **这从反面印证了 Lead 的规则**：mlsys 的课件文本层**只能用** `pdftext3.py` 的 `.faithful.txt`。
> 另外 faithful 里每页都带页脚 `Automated Approaches to Accelerate Machine Learning`，核对时已排除。
> **行号注意**：faithful 文件里含有换页符等控制字符，`Select-String` 与 `Get-Content` 报的行号**会差几行**；
> 所以本记录的引用一律以**幻灯片标题 + 逐字原文**为准，行号只作辅助。

---

## 结论

**P0（事实错误）：0 条 ｜ P1（易误解/依据不足）：0 条 ｜ P2（措辞）：3 条**

本讲的数字全部回源命中（这是本讲最容易出错的一类，逐条列在下面）；四处**讲次指路**用课程排期核对，**全对**。
P2 两条都属「解释性内容没有出处标记」，不是判错。

---

## 已核对通过（逐条附幻灯片标题 + 逐字引用）

| 正文 | 源（幻灯片 · 逐字引用） | 结果 |
| --- | --- | --- |
| L22/L26 课件把 ML 系统拆成**七层**，并按「谁在管」分成三组（上二＝模型结构；中二＝自动微分与图级改写；下三＝并行化、内核生成、显存优化） | `An Overview of Machine learning Systems` / `An Overview of Deep Learning Systems` 页的栈：**`ML Model` / `Network` / `Automatic Differentiation` / `Graph-Level Optimization` / `Parallelization` / `Kernel Generation` / `Memory Optimization`** | ✅ **正好七层**，分组也与页面的三组一致 |
| L46 第 1 层的说明：「把反向的计算图自动建出来」；L54「第 4 讲会把这一层展开」 | `Layer 1: Automatic Differentiation` 页：`backward computation graph`；`mlsys-site-lectures.yml`：第 4 次课 = `Automatic Differentiation`（`/slides/04-automatic-differentiation.pdf`） | ✅ 引文与讲次都对 |
| L60 引文 `A collection of simple trainable mathematical units that work together to solve complicated tasks.`；两个单元是张量与张量代数算子 | `Recap: DNNs as Computation Graphs` 页：`Collection of simple trainable mathematical units that work together to solve complicated tasks` / `A tensor algebra operator (e.g., convolution, matrix …)` | ✅ 逐字对应 |
| L88/L90 融合推导：卷积 `Y = Conv2D(X, W)`；逐通道归一化 `Z = (Y − R) / P`，`R`、`P` 是与输入无关的常量；合成后 `Z = Conv2D(X, W2) + B2` | `Example: Fusing Convolution and Batch Normalization` 页：`W, B, R, P are constant pre-[computed]` | ✅ 页题、变量名与「R/P 是预计算常量」都对（**公式本身的字形在幻灯片里是排版过的数学对象**，我核到的是变量与常量语义，见「我核不到的」） |
| L100/L102 **约 200 条规则 / 约 53,000 行 / 其中约 4,000 行只为优化卷积** | `Current Rule-based Graph Optimizations` 页：`TensorFlow currently includes ~200 rules (~53,000 LOC)`；`Limitations of Rule-based Optimizations`（可扩展性那页）：`TensorFlow currently uses ~4K LOC to optimize convolution` | ✅ **三个数字全部命中**（源写作 `~4K`，我用 `4[,.]?000|4k` 两种写法才检索到——这条提醒：**核查数字要连同它的书写形式一起换着搜**） |
| L104 规则库举的三个例子：融合卷积与激活、融合卷积与归一化、融合多个卷积 | 同页：`Fuse conv + relu` / `Fuse conv + batch normalization` / `Fuse multi. convs` | ✅ 三条逐字对应 |
| L110/L112 三个局限：鲁棒性、可扩展性、性能 | 三页标题均为 `Limitations of Rule-based Optimizations`，内容分别为：`Experts' heuristics do not apply to all models/hardware`（Robustness）；`New operators and graph structures require more rules`（Scalability）；`Miss subtle optimizations for specific models/hardware`（Performance） | ✅ **三条逐条对应** |
| L114 两句真实抱怨：`the training speed is about 20% slower`、`With XLA, my program is almost 2x slower than without XLA` | 鲁棒性那页：`the training speed is about 20% slower` / `With XLA, my program is almost 2x slower than without XLA` | ✅ 逐字对应（两个数字：20%、2x 都对） |
| L116 「课件给的证据就是那约 4,000 行：它只覆盖了卷积一个算子」 | 见上：`~4K LOC to optimize convolution` **正好出现在可扩展性（Scalability）那一页** | ✅ 证据与论点匹配（不是张冠李戴） |
| L122 ResNet 案例的引用 | `Recap: DNNs as Computation Graphs` 后的案例页：`He. et al. Deep Residual Learning for Image Recognition, 2015` | ✅ 作者与年份都对 |
| L126 四步变换：放大卷积 → 拆分再融合 → 融合卷积与加法；其中一步标了 `(Decrease performance)` | 该案例的三页上分别有 `Enlarge convs` / `Split` / `Fuse convs` / `Fuse conv & add`，且**每一页都带 `(Decrease performance)`** | ✅ 四步与那句标记都对 |
| L136/L138 同一张图：**V100 上快 30%、K80 上慢 10%** | 该页：`The final graph is 30% faster on V100 GPU but 10% slower on K80 GPU.` | ✅ **两个百分比、两块卡、方向全对** |
| L140 引文 `Infeasible to manually design graph optimizations for all cases.` | `Infeasible to manually design graph optimizations for all cases` | ✅ 逐字对应 |
| L144/L146/L148/L150 出路：把图优化自动化，`Generator` 提出候选、`Verifier` 证明等价 | `Automated Graph Optimizations` 页（同页还有 `ML Operators`、`Graph Architectures`、`Hardware Backends`；`Generator`、`Verifier` 两个词在同一页上，两种检索方式都命中） | ✅ 两个角色存在、分工与页面一致 |
| L154「这条路线在第 19 讲会展开」 | 按 `mlsys-site-lectures.yml` 的**上课次序**（跳过 No Class / 春假）数到第 19 次课 = `Advanced topics: ML Compilation`（`/slides/advanced-topic-mlc.pdf`，03/30） | ✅ 指路对（自动图优化属于 ML 编译这一块） |
| L160/L162 SGD 的三步：前向传播 / 反向传播 / 权重更新 | `Recap: Stochastic Gradient Descent (SGD)` 页：`Train ML models through many iterations of 3 stages` / `1. Forward propagation: apply model to a batch of input samples and run calculation through operators to produce a prediction` / `2. Backward propagation: run the model in reverse to produce error for each trainable weight` / `3. Weight update: use the loss value to update model weights` | ✅ **三条逐字对应** |
| L164 数据并行（切数据、各自算梯度、再汇总） | 该页：`1. Partition training data into batches` / `2. Compute the gradients of …` / `3. Aggregate gradients` | ✅ 三条对应 |
| L164 模型并行（把模型拆成子图分给不同设备，代价是卡间传中间结果） | 该页：`Split a model into multiple subgraphs and assign them to different devices` | ✅ 逐字对应 |
| L166 讲次指路：数据并行 = 第 9 讲、模型并行 = 第 10 讲 | 排期第 9 次课 = `ML Parallelization (Data Parallelism and Zero Redundancy)`（`/slides/08-…part1.pdf`）；第 10 次课 = `ML Parallelization (Model and Pipeline Parallelism)`（`/slides/09-…part2.pdf`） | ✅ **两处都对**（页面用的是**上课次序**，不是文件名前缀） |
| L172 手写算子库：卷积走 `cudnnConvolutionForward()`、矩阵乘走 `cublasSgemm()`，都在 cuDNN、cuBLAS 里 | `Existing Approach: Engineer Optimized Tensor Programs` 页：`Hardware vendors provide operator libraries manually developed by software/hardware engineers` / `cudnnConvolutionForward` / `() for matrix multiplication` / `cuDNN,` / `cuBLAS` | ✅ 两个函数名与两个库名都对 |
| L176 手写路线的两个问题写「在课件上」：新算子拿不到即时支持、手写内核不一定最优 | 同页后两行：`Cannot provide immediate support for new operators` / `Increasing complexity of hardware` / `written kernels are suboptimal` | ✅ 逐字对应 |
| L176 自动代码生成的好处：新算子马上有实现、往往比手写的更快 | `Automated Code Generation` 页：`Immediate support for new operators` / `Better performance than hand-[written]` / `Automated search for performant [programs]` | ✅ 好处两条对应 |
| L184 课件判断：能训多大的模型由 GPU 显存决定，更大的模型通常效果更好 | `GPU Memory is the Bottleneck in DNN Training` 页：`The biggest model we can train is bounded by GPU memory` / `Larger models often achieve better predictive performance` / `Extremely critical for modern accelerators with limited on[-chip memory]` | ✅ 逐字对应 |
| L184 原因：前向每一层的中间结果都要留到反向用 | 同页：`Need to keep all intermediate results alive` | ✅ 逐字对应 |
| L188 讲次指路：第 11 讲会讲两种省法，重算与换出 | 排期第 11 次课 = `Memory Optimizations: Tensor Rematerialization and Offload`（`/slides/11-memory-optimization.pdf`） | ✅ **「重算＝rematerialization、换出＝offload」逐词对上** |

---

## P2 · 措辞

### P2-1 L42 的「多出一两个数量级」是一个量化断言，课件里没有出处

正文 L42：「一块现代加速器每秒能做的浮点运算，往往比它每秒能喂进去的数据**多出一两个数量级**，于是「算得快」经常被「喂不饱」卡住。」
- **我找过的范围与检索词**：本讲 faithful 全文；`HBM|DRAM|CPU|GPU|node|FLOP|bandwidth|arithmetic intensity` ⇒
  只命中 `GPU 1 / GPU 2 / GPU N`、`each batch on a GPU`、`across GPUs`、`GPU Memory is the Bottleneck…` 等，
  **没有找到算力与带宽比值这类说法**。
- **裁决**：**P2**。这句话本身是「内存墙」的标准结论、方向也对；但它是本页少见的**带量级的具体断言**，
  而本讲课件文本层里没有出处（**也可能是纯图页/页面上的一句话，文本层抓不到** —— 所以我不判 P1）。
- **修在**：改成「算力增长通常快过喂数据的带宽（内存墙）」，或注明这句是我们的补充。

### P2-2 若干「机制级解释」没有出处标记（溯源那句其实已经覆盖，但读起来像课件原话）

页面 L204 的溯源写的是（**一般条款**，用了「例如」）：
> 「课件未展开的推论（例如「融合之所以合法是因为两步都是仿射的」「省内存带宽等于省时间」这类归纳），属于 CourseLingo 的讲解，不当作原文引用。」

按这个条款，下列内容**不算漏声明**；但它们都以**陈述句**出现，读者可能当作课件的展开。逐条列出供作者决定是否加一句提示：

| 位置 | 页面说 | 源里有的 |
| --- | --- | --- |
| L106 | 「融合卷积与归一化要求归一化的参数确实是常量，融合多个卷积要求中间张量只被这一处用到」 | 只有三条规则名（`Fuse conv + batch normalization` 等），**前置条件是我们的解释** |
| L128 | 卷积核形状 → 数据复用率 → 不同 GPU 上方向不一致 | 只有 `Enlarge convs` / `Split` 两个动作名 |
| L142 | 规则之间会互相干扰、应用顺序也变成要枚举的东西 | 源只说 `Infeasible to manually design graph optimizations for all cases.` |
| L154 | 验证本身要花钱、证明可能比一次改写贵得多 | 源只有 `Generator` / `Verifier` 两个词 |
| L178 | 一个算子要跑得快得同时决定分块大小、片上缓存、每线程算几个输出、读取顺序 | 源说的是 `Increasing complexity of hardware` + `written kernels are suboptimal` |
| L186 | 显存里要同时装下权重、梯度、优化器状态与一批中间结果 | 源只有 `Need to keep all intermediate results alive` |

⇒ 这些都是**业界准确的常识**、内容没问题；**建议**在溯源那句里把「机制解释」也点一下（一句话），或在这几处各加「我们补一句」。

### P2-3 `introduction-to-mlsys-11.svg` 的 `desc` 里有一个用错的词：「候选与**原因**等价」

- 该图的 `desc` 写：「…再让验证器证明候选与**原因**等价，只有验证通过的才交给图优化器落地。」
- 同一张图的**可见文字** T09 写的是「证明**两张图**等价」✅（这才是对的），正文 L150 也写「由它证明变换前后两张图算的是同一件事」✅。
- ⇒ **`desc` 里的「原因」应为「原图」**（与可见文字、正文都对不上）。这是一处**读屏/搜索会碰到、看图不会碰到**的错误 —— 恰好是我这类核对要抓的。
- **修在**：把 `desc` 的「候选与原因等价」改成「候选与**原图**等价」。

---

## 我核不到的（诚实记录）

> 按 `附录十四`：**「我没搜到」不等于「源材料没有」。** 下面的主张我**没有**找到源材料依据 ⇒ 我不能说它对或错。

1. **L36/L38 的训练节点构成**：「一个 CPU 和四块 GPU，每块 GPU 自带 HBM 显存，主机侧另有 DRAM」以及 HBM/DRAM 的「离计算单元近 ↔ 带宽高、容量小」这条层级关系。
   **范围与检索词**：本讲 faithful 全文；`HBM|DRAM|CPU|node|Node|memory hierarchy|bandwidth` ⇒ **0 命中**（只有 GPU 相关的若干行）。
   ⇒ 这一页在文本层里**没有对应的文字**（很可能是一张纯图/示意图页），**我核不到节点里有几块 GPU、有没有 CPU、用的是不是 HBM**。
   页面 L36 的配图是我们自绘的，所以这条只能由看过该页图的人定案。
2. **L88/L90 融合公式的逐字字形**：我核到的是幻灯片标题（`Example: Fusing Convolution and Batch Normalization`）与常量集合（`W, B, R, P are constant pre-…`），
   **`W2 = W / P`、`B2 = B / P − R / P` 这两条等式本身的排版字形**在 faithful 文本里是以数学对象形式出现的，我**没有**逐字核到（我核到的是它们与常量语义、与「两步仿射可合并」的一致性）。
3. **faithful 的行号**：该文件含换页符，不同工具报的行号会差几行（我实测过 `Select-String` 与 `Get-Content` 对同一页的同一处给出不同行号）
   ⇒ 本记录**不把行号当唯一坐标**，一律给「幻灯片标题 + 逐字引用」。**下一份记录我会一开始就用标题定位。**
4. **配图几何**：不在本次范围（Lead 说该课配图另有视觉复核）。
5. **`(Decrease performance)` 标在哪一步**：源里这个标注我数到 **3 处**（三页都在画同一串变换、标注跟着图重绘），
   而正文 L126 说「课件在**其中一步**专门标了…」，图 `introduction-to-mlsys-9.svg` 的可见文字则**点名**「课件标注：**放大卷积**这一步会掉性能」。
   **「到底是哪一步」我在文本层里无法唯一确定** ⇒ 记为核不到（检索词：`Decrease performance`；范围：本讲 faithful 全文）。
   如果作者有该页的渲染图，建议顺手确认一次图里那句点名是否准确。

---

## 覆盖面（附录十二）

- **已验**：七层栈的构成与分组；三个数字（200 / 53,000 / 4K）；三条规则例子；三个局限（含 20%、2x 两句抱怨）；ResNet 引用与四步变换（含 `(Decrease performance)`）；
  V100 30% / K80 10%；`Infeasible…` 引文；`Generator`/`Verifier`；SGD 三步；数据并行三步 + 模型并行一句；
  cuDNN/cuBLAS 两个函数名；手写路线两个问题 + 自动代码生成两个好处；显存瓶颈四句；
  **四处讲次指路（第 4、9、10、11、19 讲）全部按排期核对通过**；14 张配图的文字与 `desc`/`title` 与正文一致性。
- **未验**：机检指标；配图几何；上面「我核不到的」4 条（其中第 1 条是本讲**唯一**实质缺口）。

---

**核对人声明**：本记录只覆盖开头那个哈希的版本（`2B3EBEC0F45D454B`）。按附录五，对其它版本的结论不成立。
本记录只读正文、不修改任何 `content/` 文件；`status` 由 Lead 处理。
