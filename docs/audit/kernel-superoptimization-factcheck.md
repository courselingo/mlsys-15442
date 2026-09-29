# 事实核对 · mlsys-15442 第 20 讲 ML 超级优化
- 核对人：非作者
- 核对日期：2026-09-29
- 被核对版本：content/20-kernel-superoptimization/index.md，归一化 SHA256 前16 = `49D8A7086B72FBEF`（全文 19,430 B）
- 源材料：`_sources/mlsys-15442/evidence/mlsys-slide-18-kernel-superoptimization.pdf.faithful.txt`（32,694 B；**394 个 NUL 字节** ⇒ `read` 按二进制拒读，改用逐行读取）+ 原件 `mlsys-slide-18-kernel-superoptimization.pdf`（**目视渲染**，pypdfium2 5.13.0，scale=3）
- 抽取器与锚词（按说明第 ② 条先试探）：抽出器 = `.faithful.txt`（本课程规定）。
  `Kurzweil` / `Mirage` / `Schwartz` / `FlashDecoding` / `Triton` / `RMSNorm` 全部命中 ⇒ 本文件**可以**下否定性结论；但本文件**确实**有逐字符错位（见下），凡「错位区」内的否定性结论我在正文逐条标注。
- ⚠️ **本讲的 `===== PAGE =====` 块数 ≠ PDF 页数，而且差法不是常数**：faithful **41 块**，原件 `pdfium.PdfDocument` 实测 **39 页**。
  用 `pypdfium2` 逐页读页脚数字后定出真实对应关系：
  - faithful 的 **块 k ↔ PDF 第 (k−4) 页**（k≥5 时成立）。
  - `faithful` 里**有 3 页正文整段丢失**（只剩标题栏与页脚，图表与代码全无）：**PDF p10 / p21 / p34**（正文分别应为 `Abstract Expression-Guided Search`、`How to Verify Equivalence between μGraphs?`、`Probabilistic Equivalence Verifier`）。⇒ 本记录一律用「**幻灯片标题 + 逐字原文**」定位，页号只作辅助，并在引用受损页时**以原件目视为准**。
  - 另有 3 页**全是图、文字层为空**（PDF p10 的图形区、p26、p39 的一部分），PDF p19 只剩 `1 | 1 | 1` 之类数字；这些我未据此下结论。
- ⚠️ **★★ 一条对后续核对者有用的新事实**：**第 3、5、7、8、9、22、23、24、25、26、27、28、29 等页标题下方有逐字符错位**（+0x1D 量级的字形偏移），例如 PDF p29 `Probabilistic Equivalence Verifier` 副标题在 faithful 里是 `,GH  :   XVH  UDQGRP  LQSXWV  LQ  ILQLWH  ILHOGV…`，PDF p24 是 `5HSUHVHQW D WHQVRU¶V FRPSXWDWLRQ…`，PDF p32 是 `)DVWHU //0 ,QIHUHQFH…`，PDF p27 是 `5HGXFH JHQHUDWRU¶V VHDUFK VSDFH`，PDF p19 是 `WKRXVDQGV OLQHV RI &8'$ FRGH : D IHZ OLQHV RI`。
  ⇒ 本文件是**同一文件内「部分页错位、部分页正常」**（与 `eth-ca` 第 9 讲那条「按页静默丢失」同型）。**错位页上的英文短语检索将 0 命中，而中文语境里它其实存在。** 本记录凡涉错位页的判断，均以**原件目视**或**错位解码**（+0x1D）为准。

## 结论
P0（事实错误）：**3** 条 ｜ P1（易误解/依据不足）：**3** 条 ｜ P2（措辞）：**4** 条

## P0 · 事实错误

| # | 位置 | 正文说 | 源材料说 | 依据（逐字引用 + 幻灯片标题） |
| --- | --- | --- | --- | --- |
| P0-1 | 正文第 168 行 | 「课件的两组数字说明了这一步的效果：同规模的问题，用抽象表达式之后搜索的**规模从三百多降到十几**。这个倍数不是靠更快的机器拿到的，而是靠换了一种表示。」 | 那两组数字是**搜索耗时（分钟）**，不是「规模」；而且是 **332.2 分钟 → 1.0～3.1 分钟**，**没有任何「十几」，量级是百倍不是二十倍**。 | 幻灯片标题 `Challenge: Extremely Large Search Space`（PDF p20）与 `Abstract Expression Significantly Improves Scalability`（PDF p27）。**原件目视** p20：纵轴逐字为 `Search Time (minutes)`，横轴逐字为 `Max # operators in a thread block graph`，两条折线点值 `12.8` 与 `332.2`，图内标注 `The example μGraph needs 11 operators`。**原件目视** p27：图例逐字为 `w/o Abstract Expression` 与 `w/ Abstract Expression`；橙线点值依次为 **`1.0`（5 个算子）/ `1.6`（6）/ `2.5`（7）/ `2.5`（8）/ `2.8`（9）/ `2.8`（10）/ `3.1`（11）/ `3.1`（12）**。faithful 文本层同页逐字为：`12.8 \| 332.2 \| 1.0 \| 1.6 \| 2.5 \| 2.5 \| 2.8 \| 2.8 \| 3.1 \| 3.1 \| 1 \| 10 \| 100 \| 1000 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Search Time (minutes) \| Max # operators in a thread block graph \| w/o Abstract Expression \| w/ Abstract Expression`。⇒ 页面把**纵轴（耗时，分钟）**读成了**规模**，并把橙色线在 5→12 个算子区间的取值范围（1.0～3.1）说成「十几」。 |
| P0-2 | 正文第 110 行 | 「课件举的例子是 RMSNorm 与矩阵乘：现有系统之所以启动两个内核，原因就是**中间结果放不下共享内存**，而共享内存是块内共享的、容量有限。」 | 源说的是 **`;`（即 γ，RMSNorm 的缩放系数）放不下共享内存**，不是「中间结果」。 | 幻灯片标题 `Example: RMSNorm & MatMul in LLMs`（PDF p12）。faithful 逐字为：`Kernel graph \| Example: \| RMSNorm \| & \| MatMul \| in LLMs \| Existing systems launch two kernels since \| ; \| does not fit in shared memory`。⇒ `since ; does not fit in shared memory` 的主语是那个 `;`（课件公式里的 γ），**不是**中间结果。（课件同页还列了 `Performance issues: 1. No shared memory reuse 2. Kernel launch overhead`。）配图 `figures/kernel-superoptimization-8.svg` 第 4 行 `desc` 与第 2817 行文字「因为共享内存放不下，只能分成两个内核」同样未点明是谁放不下 ⇒ 与正文同错。**注**：PDF p34 有 `Programming Abstraction for H100`；此处依据的是 p12。 |
| P0-3 | 溯源第 211 行 | 「课件在这一讲里引了**若干**外部材料，本页照原样标注，且均未转载其原图：单位成本算力那条长期曲线（课件标注 Ray Kurzweil 的《The Singularity Is Near》，2005，并在图上标出「2023 年超过人脑算力」这个预测）……」 | Kurzweil 那条曲线的归属与年份都对，但**正文里引用的这个时间是绿字「2023」，而课件图上的 2023 指的是「超过人脑算力」**；更关键的是页面把**同一张第三方图**既说成「照原样标注」又说「未转载其原图」，而**成稿配图的 `desc` 与正文都在转述该图的数值与结论**——这是「归属已标但使用方式与声明不符」。此外该页在页面里被登记为「引了若干外部材料」，但**正文正文中并没有为 Kurzweil 这条曲线标出来源**（只在溯源里出现）。 | 幻灯片标题 `Compute Per Second Per Dollar`（PDF p3）。**原件目视** p3：整幅是 Kurzweil 原书插图（含 `Analytic engine` / `Colossus` / `UNIVAC I` / `Apple II / Power Mac G4` 等分段），页脚逐字为 `* Ray Kurzweil. The Singularity Is Near: When Humans Transcend Biology. 2005`，右侧绿字为 `Surpass human brainpower in 2023`；faithful 同页逐字为 `Compute Per Second Per Dollar \| * Ray Kurzweil. \| The Singularity Is Near: When Humans Transcend Biology. \| 2005 \| Surpass human \| brainpower in \| 2023`。正文第 38–40 行转述了该图（「跨越了几十年」「预测的某个时间点」）但**未在正文标注来源**；配图 `kernel-superoptimization-2.svg` 的 `desc`/文字也没提 Kurzweil。 |

## P1 · 易误解或依据不足

| # | 位置 | 正文说 | 问题 | 依据 |
| --- | --- | --- | --- | --- |
| P1-1 | 配图 `figures/kernel-superoptimization-8.svg`（第 2817 行及 `desc`） | 「跨层之间：**需要启动不同的内核**」 | 源只说「同一层的算子可以合并」，**没有**「跨层就要另起内核」这条规则。层级图（`Thread graph` / `Thread block graph` / `Kernel graph` / `GPU-level / SM-level / Thread-level`）讲的是**抽象的层级**，不是「内核边界的位置」。这一格是页面补的因果，而它在配图里以断言形式出现。 | 幻灯片标题 `μGraphs: Hierarchical Graph Representation`（PDF p11）。faithful 逐字含 `Thread \| GPU Device \| SMs \| CUDA Cores / Tensor Cores \| AllReduce \| Matmul \| GraphDef \| Op \| Kernel graph / Computation Graph \| Thread block graph \| Input \| Iterator \| Reshape \| Thread graph \| Exp \| Sum \| Output \| Accum`；全 deck 检索 `different kernel` / `across level` / `cross level` → 0 命中。 |
| P1-2 | 正文第 50 行 | 「第 **15** 讲讲过两个 SM 组成**簇**」 | **指路没错，但与本页自己的课件号约定冲突**：本页溯源第 209 行声明「本页一律用仓库讲次号指路」，而仓库第 15 讲（`tirx-gemm`）确实讲了「相邻的两个 SM 可以互读对方的共享内存」+「每个 SM 228 KB」（我逐字核过 `content/15-blackwell-tirx/index.md` 第 36、176–186 行）——**所以在「用仓库讲次号」这套体系下它是自洽的**。问题是课件原件里的**同一硬件事实**出现在 PDF p7/p33 的 `Processing Cluster` 页上，读者若按课件号查找会对不上；且本页第 112 行同时引「第 15 讲的 228 KB」，两处都依赖同一条仓库编排。**建议**：不是错，但应在溯源里像第 8 讲那样再点一次「15 = tirx-gemm」。 | `content/15-blackwell-tirx/index.md` 第 36 行「每个 SM 228 K…」、第 182 行「相邻的两个 SM 可以互读对方的共享内存」；本页第 209 行「课件号的对照见第 8 讲溯源」。 |
| P1-3 | 正文第 136 行 | 「更难的是候选空间**没有明显的连续结构**：改一个分块尺寸只是挪一格，而换一种算子组合方式则跳到另一类图上。」 | 这是页面的自撰刻画。源在 `Challenge: Extremely Large Search Space` 页给的证据恰恰是**离散跳变**（横轴 `Max # operators in a thread block graph` 取整数值、纵轴耗时在对数坐标上从 12.8 跳到 332.2），可以说支持「组合爆炸」，但「连续结构/挪一格」这组对立词源里没有。溯源第 213 行的推论清单**未登记**这一条。 | 见 P0-1 的逐字引用；全 deck 检索 `continuous` / `discrete` / `structure` → 0 命中有效句。 |

## P2 · 措辞

| # | 位置 | 正文/配图 | 说明 |
| --- | --- | --- | --- |
| P2-1 | **全篇**（正文第 104、106、108、110、112 行等）与**全部 14 张配图** | 页面与配图一律写「图」「分层图」，源里一律写 **`μGraph`**（希腊字母 μ） | 源每一页都写 `μGraph`（`μGraph Generator` / `μGraph Optimizer` / `Best Discovered μGraph for RMSNorm & MatMul` / `Best μGraph for GQA` / `Key Challenges to Discover High-Performance μGraphs` / `Mirage Discovers Hardware-Customized μGraphs`），**没有一处写 plain `Graph` 当作这套表示的专名**。页面译成「图」后，读者无法用「μGraph」回源检索。建议至少在首次出现处给出 `μGraph`。 |
| P2-2 | 配图 `…-11.svg` 第 2137 行 | 「生成器在**算子**、线程块、线程三个层级上展开」 | 源的两处措辞都不是「算子」：`μGraph Generator` 页逐字为 `Operators at the kernel, thread block, and thread levels`（层级名是 **kernel**/thread block/thread），`Can Algebraic Properties Guide Search?` 页的三列表头逐字为 **`GPU-level` / `SM-level` / `Thread-level`**。⇒ 建议写「内核级、线程块级、线程级（课件亦作 GPU 级 / SM 级 / 线程级）」。 |
| P2-3 | 正文第 192 行 | 「它能在新硬件上用上**新的互联方式**，比如在 H100 上利用**处理簇**这一级做归约。」 | 源的措辞是 `Leverage **GPC-level AllReduce** to accelerate attention on H100`，并且明说是 **GPC（Graphics Processing Cluster）**这一级；页面把 `GPC` 泛译成「处理簇」且未给缩写，与源 `Processing Cluster` 的中译只差一字，读者难以回源。数字 `2.2x faster than best existing kernels` 页面未给（可接受）。 |
| P2-4 | 正文第 148、150 行 | 「图生成器负责产出候选，它会在算子、线程块、线程三个层级上展开；……最后由**后端**生成真正能跑的 GPU 内核。」 | 源两页的框只有三个：`μGraph Generator` → `Equivalence Verifier` → `μGraph Optimizer` → `Fast GPU Kernels`。页面把 `Fast GPU Kernels` 说成「后端」，是一个未标注的术语替换（源没有「后端」这个词，也没有第四个部件）。配图 `…-11.svg` 更把它画成**第四个框**「后端」。 |

## 我核不到的（诚实记录）

- **三页正文在 faithful 里整段丢失**，我改用**原件目视 + 页脚定位**补上，但**未能逐字回源**它们的文字层内容：
  - **PDF p10 `Abstract Expression-Guided Search`**：faithful 块 21 只剩 `Æ Graph Generator \| RMS Norm \| MatMul \| Mul \| Automated Theorem Prover \| A1. … \| A2. … \| Subexpression axioms \| E1. … \| Equivalence axioms \| continue the search \| prune candidate`。正文第 164 行说「它还说，Mirage 用一阶逻辑来推理这两种关系」——**这一句我在 PDF p25（`Abstract Expression`，faithful 块 25）核到了**（逐字 `Mirage uses first-order logic to reason about two relations`，且该页把两个目标标为 `Goal 2: equivalence` / `Goal 1: subexpression`），所以该句**有依据**；但**公理组 A1/A2/E1 的具体内容被错位/截断**，我**没有**逐条核对，因此页面若对这些公理有任何具体转述，我无法判定。页面**没有**转述公理内容 ⇒ 无需更正。
  - **PDF p21 `How to Verify Equivalence between μGraphs?`**：faithful 块 25 的正文部分是**错位字形**（`2 Ð ( : 5 á : 6 á ä ä á : á be a non - zero polynomial of total degree d over a finite field ( . Let N 5 á N 6 á ä ä á N á be selected randomly and uniformly from ( . Then … Sub = A " > 2 N 5 á N 6 á å á N á L r ? Q @ ( `）。可见 `Schwartz–Zippel lemma` 的**陈述被错位**。正文第 176 行只概括为「在有限域里取随机输入，用它们去检验两个图是否给出相同结果」，与**原件目视**到的 `non-zero polynomial … total degree d over a finite field` 一致，**该句有依据**；但我**没有**逐字核对引理陈述的窗口参数（这句源里本就是错位的）。页面没有给公式 ⇒ 无需更正。
  - **PDF p34 `Probabilistic Equivalence Verifier`**：faithful 块 29 保留 `Idea : use random inputs in finite fields to examine μGraph equivalence \| Random Input \| Theorem 1 : if 5 is equivalent to 6 , then 1 5 L 1 6 \| Theorem 2 : if 5 is not equivalent to 6 , then 1 5 M 1 6 with a certain probability \| L * * L R 5 Í , where 6 is the size of intermediate tensors \| Run P random tests, non - equivalent μGraphs pass all random tests with probability : s F L ; ç`。正文第 178 行「以极高概率成立」**有依据**（`Theorem 2 … with a certain probability`、`Run P random tests`）；但「出错概率随中间张量大小下降」这一条（`where 6 is the size of intermediate tensors`）页面**未提**，我未据它下结论。
- **正文第 40 行**：「课件引的那条曲线跨越了几十年，而**模型侧的变化只发生在最近十几年**，两者的时间尺度差别很大，而正是这个错位让「把算力用满」成了一件长期有价值的事。」——前半（曲线跨越几十年）**有依据**（PDF p3 横轴 1900→2045，目视确认；faithful 逐字 `1900`/`1920`/`1940`/`1960`/`1980`/`2000`/`2011`/`2020`/`2045`）。后半「模型侧只发生在最近十几年」在课件里**没有任何句子支撑**（检索 `decade` / `recent` / `years` 只命中 Kurzweil 图内的 `years` 标签）；这是解读，溯源第 213 行**未登记**。⇒ 记为依据不足（不单列 P1 条目，因它已含在「未登记的推论」这一现象里，与第 19 讲同型）。
- **正文第 26 行**「目标不是优化某一个算子，而是把『哪个式子怎么写、写成几个内核、每个内核怎么分块』这几件事放在一起搜」：源的定义句逐字为 `Optimize ML performance by simultaneously considering • Algebraic transformations • Custom GPU kernels • Schedule transformations`（PDF p8）。页面的三分说法**等价但有改写**，我判定为可接受的讲解，不列为条目。**注**：该页 faithful 块 9 的标题在错位区，我以**原件目视**（页脚 `10`）为准。
- **正文第 36 行**「课件在这一页标了两个来源，分别是 OpenAI 与 NVIDIA」：**核到**，PDF p4 逐字 `Scaling Law in ML \| Source: OpenAI \| Source: NVIDIA`。✔
- **数字逐项回源结果**（全部命中，无一条落空）：`100s` SMs / `128 CUDA cores` / `4 tensor cores` / `1K - 100K GPUs`（PDF p5）；`96 KB`（第 6 讲，`mlsys-slide-06-CUDA-programming.pdf.faithful.txt` 逐字 `96 KB of shared memory`）；`228`（第 15 讲，见 P1-2）；`2.3x faster than Triton`（PDF p38，标题 `Case 2: Optimized μGraph for LoRA (2.3x faster than Triton)`，逐字 `Fuse three matmuls and an addition into a single kernel`）；`2.2x`（PDF p16 `Best μGraph for GQA` 逐字 `2.2x faster than FlashDecoding by Eliminating redundant KV cache access / Using tensor cores more efficiently`，与 PDF p35 `2.2x` `faster than best existing kernels`）；`1.4x … 2.7x`（PDF p31 目视：`1.4x 1.6x 1.7x 2.0x 2.2x 2.7x` 对应 `QKNorm RMSNorm LoRA nTrans GQA GatedMLP`）；`exp, 3 sums, and a div`（PDF p15 逐字 `Perform attention in two kernels by decomposing softmax into exp, 3 sums, and a div`）。⇒ 正文第 190、192 行的 `2.3 倍`、`1.4 到 2.7 倍` **正确**。
- **`[[term:...]]` 词条**不在本讲页面的核对范围内，我未核对词条定义。

## 覆盖面

- **配图：14 张**（`kernel-superoptimization-1.svg` … `-14.svg`，与正文 14 处 `![...]` 一一对应，无游离图）。
  - **逐张通读：14 张全部**（`grep '<desc|<text '` 逐条读出 `desc` 与全部 `<text>` 节点；本讲我方用的是**全量读取**，因为 `desc` 不渲染、只有读出才发现问题——P0-1、P0-2、P1-1、P2-2 四处都由这一步定案）。
  - **定向检索：0 张**。
- **原件目视**（pypdfium2 渲染，产物在**课程仓库之外**：`D:\Vibe_Workspace\_scratch_mlsys21\img20\`）：第 3、7、8、15、16、20、21、27、30、31、34、36 页，共 **12 页**。P0-1、P0-3、P1-2、P2-1 的结论均由目视定案。
- **页↔块对应**：用 `pypdfium2` 逐页读页脚数字，定出 `faithful 块 k ↔ PDF 第 (k−4) 页`，并查明 **p10 / p21 / p34 三页正文整段丢失**、**p19 只剩数字**。此项本身不属于本讲页面的事实错误，但它是本讲所有定位的前提，故记在此处。
- **否定性结论的范围与检索词**（faithful 全文，逐行 UTF-8 解码 + NUL 替换）：
  - 「跨层就要另起内核」：`different kernel` / `across level` / `cross level` / `cross-level` → 0。
  - 「连续结构」：`continuous` / `discrete` / `structure` → 0 有效句。
  - 「模型侧只发生在最近十几年」：`decade` / `recent` / `years` → 仅命中 Kurzweil 图内的 `years` 标签。
  - 「调度变换 vs 计算组织」：`Schedule transformations` 命中 1（PDF p8 定义页）；`Compute organization` 命中 1（PDF p30 `output-alternating optimizations` 列表）。⇒ 源**两个词都用**，页面统一译成「调度变换」，我判定可接受、不列条目。
  - 「μGraph vs Graph」：`μGraph` 命中 **25** 次；`(^|\W)Graph(?!Def)` 型检索确认源**从不**把 plain `Graph` 当这套表示的专名用。

## 跨讲承诺（说明第 ⑩ 条）

**本讲对别人许的承诺：0 条。** 逐字检查正文与溯源，全部指路都是**回指**（第 2、6、9、10、13、15 讲），`第 2[1-9] 讲` / `下一讲` / `后面会` / `将会讲` 全部 **0 命中**。⇒ 不存在指向第 22 讲之后的、不可能兑现的承诺。

**别人对本讲的承诺（本讲是否兑现）：**
- 第 8 讲全表声明 `第 20 讲 ← 18-kernel-superoptimization`，并说「本页一律用仓库讲次号指路」。**本页溯源第 209 行已兑现**：逐字为「原文课件：https://mlsyscourse.org/slides/18-kernel-superoptimization.pdf（课件号的对照见第 8 讲溯源；本页一律用仓库讲次号指路。）」
- **★ 但你（Lead）在本轮给我的任务描述里说「第 20 讲源码文件名为 `18-kernel-superoptimization`、第 21 讲为 `19-mega-kernel`，课件号与仓库讲次号差两位」——这句话在本课上不成立，我按证据更正：** 见 `content/08-transformer-attention/index.md` 第 209–220 行的**全表**：`第 16 讲 ← 15-LLM-serving-part2`、`第 17 讲 ← 16-LLM-finetuning`、`第 18 讲 ← 16-mixture-of-experts`、`第 19 讲 ← advanced-topic-mlc（无编号）`、`第 20 讲 ← 18-kernel-superoptimization`、`第 21 讲 ← 19-mega-kernel`。**偏移量逐讲变化、不是常数**（第 20 讲是 −2，但第 16 讲是 −1、第 18 讲是 −2、第 19 讲无号）。第 8 讲原话就是「**偏移量逐讲变化，而不是一个常数**」。
- **「换出/offload」缺口**：本讲与换出无关。faithful 全文检索 `offload` / `swap` / `pinned` / `host` / `cpu` → **hits = 0**（本 deck 讲的是搜索与硬件结构，没有内存换出话题）。⇒ 本讲**没有**补上第 2 讲对第 11 讲许下的那个承诺，也**没有**对换出许下新承诺。
- **一个需要 Lead 判断的「跨讲联系」**：正文第 213 行把「融合的收益」归到「第 2 讲**和第 13 讲**」。第 2 讲确实有规则式融合（`content/02-introduction-to-mlsys` 的源 `mlsys-slide-02-introduction-to-MLSys.pdf`，PDF p10 逐字 `Current Rule - based Graph Optimizations`）。**但第 13 讲在仓库里的源是网页版 gemm（`https://mlsyscourse.org/slides/gemm/`），不在 `_sources/…/evidence/` 里**；我只在 `_sources/mlsys-15442/evidence/` 全部 20 个 `.faithful.txt` 里检索，**无法**确认第 13 讲讲过「融合的收益」。⇒ 记为**核不到**，不下对错结论。（同型问题：第 12、13、15 讲都源自网页版，不在证据目录内。）
