# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 10 讲 并行化（下）：模型并行与流水线并行

- 核对人：**非作者**（本讲任何一轮写作我都没有参与，也没有与作者 `mlsys-author` 讨论过本讲内容）
- 核对日期：2026-09-29
- 被核对版本：`content/10-ml-parallelization-2/index.md`
  归一化 SHA256 前16 = **05B1261A3C4A827D**
  （全 64 位 `05B1261A3C4A827D14A2FF491494FC62FFAEABD2B40DFD9C686FDAA907D8BC65`，**20,184 B**；
  文件本身已是 LF（`\r\n` 计数 0），归一化后长度与哈希都不变；最后写入 2026-09-29 10:48:13）
  - 15 张配图（`figures/ml-parallelization-2-1.svg` … `-15.svg`）
- 源材料（本次实际依据的，逐个列出，并说明我怎么用它）：

| # | 文件 | 用途 / 说明 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-09-ML-parallelization-part2.pdf`（**2,985,543 B**） | 权威源。**取件校验**：尾部 `\r\n2985355\r\n%%EOF`（`startxref` 指向 2,985,355 < 2,985,543）、大小**不是** 2 的整数次幂 ⇒ 判定为完整件；对象层 `/Type /Page` 34、`/MediaBox` 34、`/Pages` 1、`/Count 34` |
| 2 | 同目录 `.faithful.txt`（**21,096 B**，121 个 NUL，38 个 `===== PAGE =====` ⇒ **39 个文本块**） | **主要依据**（按项目约定用 faithful）。只读副本在 `%TEMP%`，未改源文件。按「幻灯片标题 + 逐字原文 + 文本块序号」定位 |
| 3 | 同目录 `.embedded.txt`、`text-clean/*.txt` | **一律未使用**（按规则） |
| 4 | `evidence/mlsys-slide-08-ML-parallelization-part1.pdf.faithful.txt`（43,493 B） | **专项**：核第 9/10 两讲重叠、核「上一讲」指的是谁 |
| 5 | `evidence/mlsys-site-lectures.yml`、`evidence/mlsys-course-schedule.html` | 核本讲的**周次、日期、讲者** |
| 6 | `content/08-transformer-attention/index.md`、`content/03-deep-learning-abstraction/index.md`、`content/09-ml-parallelization-1/index.md`、`glossary.toml` | 核本页的**跨讲指路**（L96/L100/L152）与 8 个不同的 `[[term:…]]` |
| 7 | `evidence/mlsys-webrepo-LICENSE.bin`（**正好 19,342 B**） | 核溯源 L224 的许可体积 |

> **定位约定**：这一份 faithful 分出 **39 个文本块**，而 PDF 对象层是 **34 页**（`/Count 34`）——差 5，
> 和上一讲那种「块数 ≠ 页数」是同一个现象。本环境没有 PDF 解析库，我没有解开这个差，
> 所以本记录一律用「**B\<n\>**＝faithful 第 n 个文本块 + 幻灯片标题 + 逐字原文」，**不写「pN = PDF 第 N 页」**。

> **文本层说明（含一个新工具）**：正文（英文句子）完整可检索，锚词 `512`、`90-95% of the computation`、
> `Mini-batch`、`One-Forward-One-Backward`、`Doesn't reduce pipeline bubble` 等都能原位命中；
> 公式与图形标注落在字形码里（例如 B27 的 `I Û P Ù L I Û P Õ L …`、B33/B36 的 `>Ì Ch`、B32 的 `9`）。
> **我把说明文件里那条 `+0x1D` 位移用上了**：`'RHVQ¶WUHGXFHSLSHOLQHEXEEOH` → `Doesn't reduce pipeline bubble`（B30 的一行隐藏标注），
> `*3LSH¶V` → `GPipe's`。但这条位移**只对这两个字体子集有效**：其余字形码（公式那批）我试了 `+0x1D`／`-0x1D` 都读不出东西，
> 所以下面凡是涉及那几批字形码的判断，我都写明「读不出」而**不下结论**。

---

## 结论

**P0（事实错误）：1 条 ｜ P1（易误解/依据不足）：2 条 ｜ P2（措辞）：4 条**

**这 1 条 P0 是跨讲指路指错了对象**（说明文件方法 ④ 点名的那类：`第 M 讲引用第 N 讲`）：
本页两处「上一讲」（＝第 9 讲）说的其实是**第 8 讲**的内容，而我用逐字检索确认第 9 讲那一页**根本没有**讲注意力。
除这一条外，本讲的数字与定义我逐个回源核过：`512 块 GPU`、`90–95% 计算量 / 5% 参数 / 95% 参数`、
`Mini-batch`、`I`/`L`、`GPipe` 的提问、1F1B 的三条描述、交错式 1F1B 的 `R` 与那句 `Reduce bubble time at the cost increased communication` **全部逐字命中**。

---

## P0 · 事实错误

### P0-1 L96 与 L100 的「上一讲」指错了对象：这两句说的内容在第 **8** 讲那一页，第 9 讲那一页全篇没有注意力

- **正文逐字**：
  - L96：「自注意力层那部分，切法**在上一讲已经出现过**：按头切开，各头本来就是独立的计算。」
  - L100：「这里也回答了**上一讲留下的一个疑问**。**上一讲说**多头注意力「计算开销更小」，当时只是列在好处里；到了这一讲，按头切分正好用上了这一点…」
- **第 8 讲那一页（`content/08-transformer-attention/index.md`）逐字**：
  - L58 小节标题：`## 多头注意力`
  - L66：「课件给的好处有两条：并行度更高，**计算开销更小**。第二条初看有点反直觉，因为分多头之后乘法的总次数并没有变少…」
  - L200（该讲自己的思考题）：「3. 多头注意力并没有减少乘法的总次数，请说明课件说的「**计算开销更小**」省的是什么。」
  ⇒ 「计算开销更小」这句**逐字**出自第 8 讲的页面，也印证在 `content/03-deep-learning-abstraction/index.md` L112 那句已登记的承诺里：
  「这一页还列了后面会展开的三个概念：自注意力、掩码注意力与多头注意力。**第 8 讲会把它们讲透**。」
- **第 9 讲那一页（＝本页的「上一讲」）**：全篇 `多头注意力`／`计算开销更小`／`按头` 命中数 **0**；
  `注意力` 只有 1 处，是 L146 那句中文习语「课件把**注意力**转回显存」，与注意力机制无关。
- **课件层面双证**（我直接用两份 faithful 数过）：
  - 第 9 讲的课件（deck 08）里 `Head`／`head`／`Self`／`Multi` 命中数**都是 0**，`Attention` 只有 1 次，是那页 Transformer 图下的引用
    `Ashish Vaswani et. al. Attention is all you need.`；
  - 「按头切开」作为**跨设备**的切法出现在**本讲自己的课件**里：B21（标题 `Multi-Head Self-Attention`）与
    B22（标题 `Parallelizing Self-Attention Layers in Transformers`，逐字 `Parallelizing across attention heads`、`Tensor model parallelism (reduce output)`）。
- ⇒ 两处都应改：要么写「第 8 讲」（并补上它是哪一页的哪句话），要么干脆删掉这层跨讲指路。
  L96 若想保留「按头切是天然的边界」这个判断，源就在**本讲** B21/B22，直接引本讲更干净。
- 注意溯源 L226 那句「本讲与前后讲次的对应关系属于我们的编排」——**编排自由不等于指路可以指错**：
  「上一讲说 X」是一句可核的事实断言。

---

## P1 · 易误解或依据不足

### P1-1 L148「课件给的两条路」漏掉源里的第三条，且两条 caveat 被换成了课件没有的两条

- **正文 L148 逐字**：「课件给的两条路是把小批次加大，或者把微批次减小。加大前者会让**每个微批次的计算量变大**，减小后者会让微批次数变多，两种都能把填充阶段的占比压下去。」
- **正文 L150 逐字**：「两条路都有上限。**加大批次受显存限制**，因为同一时刻在飞的数据变多了；**减小微批次受通信开销限制**，因为微批次太小的时候，每一轮的通信固定开销就盖过了计算本身。」
- **源（B28，标题 `Improving Pipeline Parallelism Efficiency`）逐字**：
  ```
  I: number of micro-batches in a mini-batch
  Increase mini-batch size or reduce micro-batch size
  Caveat: large mini-batch sizes can lead to accuracy loss; small micro-batch sizes reduce GPU utilization
  L: number of pipeline stages
  Decrease pipeline depth                    <- 第三条路
  Caveat: increase stage size                <- 第三条路自己的 caveat
  ```
- 三处不一致：
  1. **计数**：源在同一页给了**两条旋钮、三条路**（`I`：加大小批次 / 减小微批次；`L`：**减小流水线深度**），本页只写「两条路」，`L` 那条完全没出现（说明文件第 ⑧ 条那种计数体系问题）。
  2. **两条 caveat 被换掉**：源写的是 `can lead to accuracy loss`（加大批次）与 `reduce GPU utilization`（减小微批次）；
     本页写成「受显存限制」与「受通信开销限制」。这两条工程上也说得通，但**不是课件写的那两条**，而本页的写法让读者以为这就是课件的取舍。
  3. **机制**：「加大前者会让每个微批次的计算量变大」与源的口径对不上——源是 `Increase mini-batch size`（在小批次里放更多微批次 ⇒ `I` 变大），
     微批次本身的计算量没变。
- 建议：把源那三行与两条 caveat **逐字引**（本页 L16 自己承诺过「关键定义处给出英文原文短引」），再补 `L` 那条路与它的 caveat `increase stage size`。

### P1-2 L202 与图 `-15.svg` 把「设备不闲着」当成课件对照表里**流水线那一栏**的强项——课件那一栏的 con 恰好是「利用受限、有气泡」

- **正文 L202 逐字**：「…**流水线模型并行那一栏是「设备不闲着，但调度复杂」**。」
  **正文 L206 逐字**：「课件的对照表给每一栏都打了勾与叉，而**没有一个方案是四项全勾的**。」
  **图 `-15.svg` 的 desc 逐字**：「数据并行、张量模型并行、流水线模型并行，各自列了擅长与不擅长的**四条**…」
- **源（B33 / B36，标题 `Summary: Comparing Data/Tensor Model/Pipeline Model Parallelism`）逐字**（列顺序照文字层原样）：
  ```
  Pros（每项前有一个 ✓ 字形，文字层里是 `9`）
    Massively parallelizable
    Require no communication during forward/backward
    Support training large models
    Efficient for models with large numbers of parameters
    Support large-batch training
    Efficient for deep models
  Cons
    Do not work for models that cannot fit on a GPU
    Do not scale for models with large numbers of parameters
    Limited parallelizability; cannot scale to large numbers of GPUs
    Need to transfer intermediate results in forward/backward
    Limited utilization: bubbles in forward/backward
  ```
  B36 这一页最后还多一行逐字：`Training large models requires combining data/model/pipeline and other parallelization techniques`。
- 我读出来的两个问题：
  1. **「设备不闲着」在源的 6 条 pro 里找不到**——最接近的流水线条目是 con 里那句
     `Limited utilization: bubbles in forward/backward`（**方向相反**：课件说流水线有气泡、利用受限）。
     本页 L108-L112 那段叙事（按层切⇒设备闲置⇒流水线解决）本身与课件一致，问题只出在把它当成**对照表流水线那一栏的话**。
  2. **「四项」/「四条」我没有在源里找到对应**：源的这张表在文字层里是 **6 条 pro + 5 条 con**（共 11 条不同文字），没有「四条」这种说法。
     但要说明我的**能力边界**：`✓`／`✗` 落在哪一列属于**表格单元格对齐**，
     文字层里丢失了（faithful 只有线性文本，没有 x 坐标；本环境没有 pdftotext/mutool/qpdf，我也没有去解 PDF 的 `Tm` 坐标）。
     所以「每一栏各 4 条」**我既不能证实也不能否证**——我能证的是：文字层里没有「四条」的依据，而「设备不闲着」与源里那句 con 方向相反。
- 连带（同一张表）：L204「数据并行缺的是显存，张量并行缺的是通信带宽，流水线并行缺的是调度余量」这组映射与源的三条 con ✅ 对得上
  （`Do not work for models that cannot fit on a GPU` / `Need to transfer intermediate results in forward/backward` / `Limited utilization: bubbles…`）。

---

## P2 · 措辞

| # | 位置 | 正文 | 源 / 说明 |
| --- | --- | --- | --- |
| P2-1 | L8 / L13 / L222 | 「…（Zhihao Jia 主讲，**2026-02-17**，第六教学周）」 | 课件 B1 标题页逐字是 `2/17/2026` ✅（本页取的是课件日期）；但课程表 `mlsys-course-schedule.html` / `mlsys-site-lectures.yml` 都写 `02/16 Mon`。**周次 `Week 6` 是对的** ✅（`02/16` 与 `02/17` 都在第 6 周）。两份材料差一天，建议写成「课件标题页日期 2026-02-17（课程表为 02/16 Mon）」 |
| P2-2 | L34 | 「它擅长的地方是改动小、扩展性好：模型代码几乎不用动，加卡就能加速」 | 源 B2/B3（两页 `Recap:`）只有那张图与三步、以及「每块卡一份完整模型」那条限制，**没有**「改动小」这类评价；这是我们的判断，但溯源 L226 的三组推论里**没有登记**它 |
| P2-3 | L142 / L164 | 「8 级而只拆成 4 个微批次…**一部分设备至少有三分之一的时间在等**」「为了把 8 级流水线填满，**I 至少要到八以上**」 | 这两个例子是作者自造的（源 B27 的公式在字形码里，我读不出）。若按 GPipe 常用的 `I/(I+L−1)` 口径，`I=4, L=8` 的空档约是 `7/11 ≈ 64%`（远不止三分之一），`I=32, L=8` 约 `82%`（说「基本一直保持满载」偏乐观）。**我不用外部公式判它错**，只提示：这两个数与「填满」的措辞容易被读成课件给的量 |
| P2-4 | 溯源 L225-226 | 取材范围与推论清单都在 | 但**没有**「跨讲承诺登记」这一节（第 2 讲的页面有，逐字：「第 9、10 讲：分别展开数据并行与模型并行」）。本讲确实**兑现**了那一半（模型/张量/流水线并行）✅，但本页没登记；同时 L96/L100 那两处跨讲指路也没进任何清单（见 P0-1） |

---

## 跨讲承诺（说明文件第 ⑩ 条）

- **本讲作出的、带讲次编号的承诺：0 条**（L46「下一节会看到…」、L124「这一点后面会变成一个主要问题」都不给编号）。
- **本讲引用的别的讲次**（都要回核）：
  | 位置 | 指路 | 核对结果 |
  | --- | --- | --- |
  | L96 | 「切法**在上一讲已经出现过**：按头切开」 | ❌ 见 P0-1：第 9 讲无此内容；跨设备按头切在本讲自己的课件 B21/B22 |
  | L100 | 「**上一讲**说多头注意力「计算开销更小」」 | ❌ 见 P0-1：逐字出自第 8 讲页面 L66/L200 |
  | L152 | 「**第 5 讲**的块大小、**第 8 讲**的分块尺寸」 | ✅ 与项目编号一致（第 5 讲＝`05-…`，第 8 讲＝`08-transformer-attention`，其页面讲分块与重算） |
- **本讲兑现别人对它的承诺** ✅：第 2 讲溯源逐字登记「第 9、10 讲：分别展开数据并行与模型并行」——本讲是模型并行（张量 + 流水线）那一半，**兑现了**（只是本页没登记，见 P2-4）。
- 第 2 讲还登记了「**第 11 讲**：展开显存的两种省法（重算与换出）」——第 11 讲记录里核。

## 专项：第 9 / 10 两讲重叠与引用方向（与第 9 讲记录配套）

- **两讲是两份独立 PDF** ✅（各自 title page 页脚都是 `1`；deck 08 尾部是 Summary 页，deck 09 开头是新的标题页）。
- **重叠只有三处**，都已逐字核过：
  1. deck09 B2（`Recap: Data Parallelism`）＝ deck08 B7（`Data Parallelism`）**整页重复**（4-gram Jaccard 1.000，共享 11/11，只多标题前缀 `Recap: `）；
  2. deck09 B3（`Recap: An Issue with Data Parallelism`）＝ deck08 B26（`An Issue with Data Parallelism`）**整页重复**（Jaccard 0.929，差的就是 `Recap: `）；
  3. deck09 B18（`Example: Parallelizing Transformers`）复用 deck08 B33（`Transformer for Language Models`）的 Transformer 图（Jaccard 0.714，共享 `Encoder`/`Decoder`/`Ashish Vaswani et. al. Attention is all you need.`）。
- **引用方向**：本页把前两页写成「上一讲的结论」（L20/L30），**方向对、标法也对**（那两页在 deck 09 里就叫 `Recap:`）；
  错的是 P0-1 那两处把第 8 讲的内容记到「上一讲」头上。

## 配图（覆盖面：逐张通读 15 张，定向检索 0 张）

- **逐张通读 15 张**：把每张 SVG 的 `<text>` 节点与 `desc`/`title` 全部读出来（`desc` 不渲染，只有通读才会碰到——本讲的 `-15.svg` 那句「各自列了擅长与不擅长的四条」就是从这里读到的，也正因此进了 P1-2）。
- **有没有两张「可用文字几乎相同」**：**没有**。两两 Jaccard 最高 **0.190**
  （`-3.svg`（模型并行按层切）与 `-8.svg`（同一时刻只有一台设备在工作）共享 `层 1…层 4`／`设备 1…设备 4` 这几个标签，但内容不同），其余 ≤0.125。
- 配图里与源冲突/需注意的地方：只有 `-15.svg`（P1-2 那条）与 `-11.svg`（「两条路…前者受显存限制，后者受通信开销限制」，P1-1 那条）。
  其余 13 张逐句对回源都对得上，例如 `-6.svg` 的「九成以上的计算量／只占 5% 的参数，激活值很大」= B16 逐字 `90-95% of the computation` / `5% of the parameters` / `Very large intermediate activations`；
  `-7.svg` 的「512 块 GPU」= B23 逐字 `Scale to 512 GPUs by combining data and model parallelism`；
  `-13.svg` 的「在飞微批次数受限于流水线深度」= B30 逐字 `Limit the number of in-flight micro-batches to the pipeline depth`。

## 我核不到的（诚实记录）

1. **对照表的单元格对齐**（P1-2 里那一点）：`✓` 在文字层里是字形 `9`（B33/B36 各 6 个），`✗` 则**没有**对应字符（很可能是画出来的线，不是文字）。
   faithful 只有线性文本、没有 x 坐标；本环境没有 pdftotext / mutool / qpdf / ghostscript（我逐个查过，都没有），我也没有去解 PDF 内容流的 `Tm` 坐标。
   ⇒ 「每一栏各 4 条」「四项全勾」这类**表格结构**主张，我**不判对错**。要核这一条必须上坐标（说明文件方法 ⑥ 的做法）。
2. **B8-B11（`Comparing Data and Tensor Model Parallelism` 那几页）的通信代价公式**：文字层里是 `% âèç % Üá $`、`1 : $ Û % âèç ;` 这类字形码，
   `+0x1D`／`-0x1D` 都解不出（这两个位移只对 B30 那种字体子集有效）。
   ⇒ 本页 L62「数据并行那张图上，前向与反向两段里各块卡之间没有箭头…张量并行那张图上每一段里都画着交换的箭头」这句**图形级**描述我**没有**核到，也不否证；
   能核的是文字层的骨架：那几页的标题分别是 `Communication Cost of Data Parallelism` / `Communication Cost of Tensor Model Parallelism`，
   两个模型并行的变体写作 `Tensor Model Parallelism (partition output)` / `(reduce output)`，B11 末句逐字 `The best strategy depends on the model and underlying machine`
   —— 本页 L72/L74 的判断与这句 ✅ 一致。
3. **L96「第一层按列切、第二层按行切」**：源 B20（i=19）与 B22（i=21）的正文没有这两句（只有 `identity layer` / `reduction layer`（B20）、`Parallelizing across attention heads`（B22）与 `Tensor model parallelism (partition output)/(reduce output)` 这些标签，算式在字形码里）。
   「按列切/按行切」是 Megatron-LM 的标准做法，但**我没有在本讲文字层里找到它** ⇒ 记「定向检索未命中」，不判对错（这一页的图里可能有）。
4. **B32（`9` 与 `>Ì Ch` 那两页）**：那两页在文字层里几乎全是字形码与单字符，我读不出内容 ⇒ 不判对错。
5. **L164 的 `C`**：本页用一个自设的符号 `C` 表示「每个微批次的中间激活值显存」，源里没有这个符号（源只有 `I`、`L` 与那两个字形公式）⇒ 属我们的推论，建议登记。
6. 检索过但**本讲 faithful 里 0 命中**的写法（用于交叉验证「不是我搜不到」）：`ZeRO`、`reduce_scatter`、`allgather`、`bfloat16`、`checkpoint`
   ⇒ 那些是**第 11 讲**那一份课件的内容（`ZeRO` 与本讲只隔一讲，容易混）。本讲没有讲它们，也没有把它们说成自己的。

## 已逐条回源、未发现问题的（供作者放心，不重复计 P）

- 回顾两页：B2 逐字 `Recap: Data Parallelism` + `1. Partition training data into batches` / `2. Compute the gradients of each batch on a GPU` / `3. Aggregate gradients across GPUs`；
  B3 逐字 `Recap: An Issue with Data Parallelism` / `Each GPU saves a replica of the entire model` / `Cannot train large models that exceed GPU device memory`；L34/L36 ✅。
- 模型并行的定义：B5 逐字 `Model Parallelism / Split a model into multiple subgraphs and assign them to different devices`；L40 ✅（图里那句 `Transfer intermediate results between devices` 也在，与 L44 的「层是串行的」一致 ✅）。
- 张量并行切的位置：B7 逐字 `Tensor Model Parallelism / Partition parameters/gradients within a layer`；L56 的引用逐字一致 ✅；
  B7 的两个变体 `Tensor Model Parallelism (partition output)` / `(reduce output)` 与 L56 的「拼起来或者加起来」✅ 对应。
- 卷积 vs 全连接的两个数字：B16 逐字 `Convolutional layers: 90-95% of the computation / 5% of the parameters / Very large intermediate activations`
  与 `Fully-connected layers: 5-10% of the computation / 95% of the parameters / Small intermediate activations`；L82 ✅（两个数字都对）。
- 分工：B17 逐字 `Data parallelism for convolutional layers / Tensor model parallelism for fully-connected layers`；L84 ✅。
- Megatron-LM 的规模：B23 逐字 `Scale to 512 GPUs by combining data and model parallelism`；L98 与溯源 L225 的「512 块 GPU」✅。
- 模型并行的毛病：B25 逐字 `An Issue with Model Parallelism / Under-utilization of compute resources / Low overall throughput due to resource utilization`；L108/L110 ✅。
- 流水线的定义：B26 逐字 `Mini-batch: the number of samples processed in each iteration / Divide a mini-batch into multiple micro-batches / Pipeline the forward and backward computations across micro-batches`；L120/L122 ✅。
- 两个符号：B27 逐字 `I: micro-batches in a mini-batch / L: number of pipeline stages`；L132 ✅。
  B27 还有一条 `All stages take … to process a forward (backward) micro-batch`（中间是字形码），对应 L140 的「每个流水线级所耗时间相同」这个前提 ✅（本页把它当前提引用，是对的）。
- 显存问题与 GPipe 的提问：B29 逐字 `An issue: we need to keep the intermediate activations of all micro-batches before back propagation` +
  `GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism` + `Can we improve the pipeline schedule to reduce memory requirement?`；L160/L166 ✅。
- 1F1B：B30 逐字 `One-Forward-One-Backward in the steady state` / `Limit the number of in-flight micro-batches to the pipeline depth` /
  `Reduce memory footprint of pipeline parallelism` / `Can we reduce pipeline bubble?`，以及我用 `+0x1D` 解出的那句隐藏标注 `Doesn't reduce pipeline bubble`；L174/L176/L178 ✅
  （「不减少气泡」与源一致：本页没有声称 1F1B 减少了气泡，而是把减气泡留给交错式那一节 ✅）。
- 交错式 1F1B：B31 逐字 `Further divide each stage into R sub-stages` / `Each device is assigned two chunks. Dark colors show the first chunk and light colors show the second chunk.` /
  **`Reduce bubble time at the cost increased communication`**；L188/L190 ✅（这句正是「把空档压小、代价是通信变多」的逐字来源，连原文少写的 `of` 都在）。
- 收束：B36 逐字 `Training large models requires combining data/model/pipeline and other parallelization techniques`；B39 标题 `Example: 3D parallelism in DeepSpeed`（页面上还有 deepspeed 博文链接）；L204/L208 ✅。
- 溯源 L224 的许可体积：`mlsys-webrepo-LICENSE.bin` 正好 **19,342 B** ✅。
- 8 个 `[[term:…]]`（`data-parallelism`、`kernel`、`throughput`、`latency`、`ml-framework`、`compute`、`hardware-accelerator`、`machine-learning-system`）在 `glossary.toml` 里都有对应条目 ✅。
