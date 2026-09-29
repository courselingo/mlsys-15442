# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 1 讲 Why ML Systems?

- 核对人：**非作者**（复用 mit-6.5840 七讲记录的核对者身份 `mit65840-reviewer`）
- 核对日期：2026-09-29
- 被核对版本：`content/01-why-ml-systems/index.md`
  归一化 SHA256 前16 = **6CBE59318BBAF47B**
  （全 64 位 `6CBE59318BBAF47BADC48C78FC98CEB7FD87529B6D1D1F75C118A215DA875F4B`，16145 B，最后写入 2026-09-29 9:45:04）
- 源材料（逐个列出，并说明我怎么用它）：

| # | 文件 | 用途 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-01-course-introduction.pdf.faithful.txt`（1482 行，16492 B） | **主要依据**：Week 1 课件（`https://mlsyscourse.org/slides/01-course-introduction.pdf`）的 **faithful 文本层**（`_sources/_audit/pdftext3.py` 产出），带 `===== PAGE =====` 分隔 |
| 2 | `_sources/mlsys-15442/evidence/mlsys-slide-01-course-introduction.pdf.embedded.txt` | 交叉核对（原始内嵌抽取；faithful 更完整，见下） |
| 3 | `_sources/mlsys-15442/evidence/mlsys-slide-01-course-introduction.pdf` | 原件（1624658 B），仅用于确认页数/存在性，未解析图像 |

> **文本层说明（按 Lead 的规则办的）**：本讲**一律用 `.faithful.txt`**，**没有用 `text-clean/*.txt`**（那一份对同一 PDF 是 201157 B 的
> 词内碎片产物）。我先验证了 faithful 可读：`Machine Learning Systems`、`MLSys as a Research Field`、
> `Why Study Machine Learning and Systems?`、`MLSys: The New Frontier of Machine Learning Systems`、`MLSys tracks at Systems/DB conferences`、
> `MLSys.org`、`100 lines of python`、`44k lines of code`、`The project did not work out in the end.` 等字符串都能原样检索到 ✅。
> 另外每页都带同一行页脚 `Automated Approaches to Accelerate Machine Learning`（讲者自己的研究组名），我在核对时把它排除。
> 引用的行号 = **faithful 文件里的原始行号**。

---

## 结论

**P0（事实错误）：0 条 ｜ P1（易误解/依据不足）：1 条 ｜ P2（措辞）：1 条**

本讲是「为什么」型的导论，具体数字与年份密集（时间轴 5 个年份、2010 项目那张代码表的 4 个数、AlexNet 的 3 栏配料表、100 行 vs 44k、评分 45/45/10）。
**这些我逐个回源核过，全部命中，没有发现与源冲突的陈述。** 唯一一条 P1 是**出处标记**问题（内容本身准确）。

---

## 已核对通过（逐条附 faithful 行号 + 逐字引用）

| 正文 | 源（faithful 行号 · 逐字引用） | 结果 |
| --- | --- | --- |
| L22 行人检测任务：`X%` 准确率 + `Y ms` 延迟预算 | **L672–699**：`Question / Need to improve self-driving car's pedestrian detection to be X-percent accurate, at Y-ms latency budget` | ✅ 逐字对应（X%/Y ms 的形状就是课件原样） |
| L38 引文 `Many algorithms we use today are created before 2000.` | **L157–161**：`Many algorithms we use today / are / created before 2000` | ✅ 逐字对应（课件被版面断行） |
| L40/L42 时间轴五个节点：1958 感知机 / 1986 反向传播 / 1992 支持向量机 / 1998 卷积网络 / 1999 梯度提升树 | **L105–155**：`1958 … Perceptron`、`1986 … Backprop`、`1992 … Support Vector Machine (SVM)`、`1998 … ConvNet`、`1999 … Gradient Boosting Machine (GBM)` | ✅ **5 个年份 + 5 个名称全对** |
| L46 「算法还不够好解释不了后来发生的变化」 | 由 L157–161 的引文直接推得 | ✅（属页面自己的推论，已在 L179 溯源中声明为我们的归纳） |
| L50/L52 2000–2010 是数据的一段；2004 年 MTurk | **L170–205**：`2000 ± 2010: Arrival of Big Data`、`2004 … MTurk`、`Data serves as fuel for machine learning models` | ✅ 年份与定性都对 |
| L54 2006 年之后是算力与规模的一段；2016 tensor core；2017 之后的公有云 | **L214–255**：`2006 ± Now: Compute and Scaling`、`2016 … TensorCore`、`2017 … Public cloud` | ✅ 两个年份与两个名词都在同一页（**年份与名词的绑定见「我核不到的」**）；「2017 年**之后**」的措辞见 P2-1 |
| L58 三条横条长度刻意不同 | 本页自绘 SVG 的排版说明 | ✅ 不适用（我们自己的图） |
| L62 三根支柱：ML 研究、数据、算力 | **L262–296**：`Three Pillars of ML Applications`、`ML Research`、`Data`、`Compute` | ✅ 三个名称逐字对应 |
| L74 AlexNet 论文标题 | **L317**：`ImageNet Classification with Deep Convolutional Neural Networks.`（Krizhevsky et al., Year 2012） | ✅ 逐字对应 |
| L78/L80 AlexNet 三栏配料表：方法＝SGD/Dropout/ConvNet/初始化；数据＝100 万张带标注图像；算力＝两块 GTX 580、训练六天 | **L307–350**：`Case Study: Ingredient of AlexNet` / `SGD` `Dropout` `ConvNet` `Initialization`（`Methods`）/ `1M labeled images`（`Data`）/ `Two GTX 580`、`Six days`（`Compute`） | ✅ **三栏逐项对应** |
| L82 「两块 GTX 580 是消费级显卡，单卡显存装不下当时的网络…**（这一句属于背景补充，课件只写了「两块 GTX 580」）**」 | 源该页只有 `Two GTX 580`（无显存、无切分说明） | ✅ **事实与标记都对**：课件确实只写了卡型号，页面把越界的部分显式标成了背景补充（这正是本轮作者按 Lead 要求补的那处） |
| L90 2010 年的「第一个深度学习项目」：一个模型变体约 44k 行，含为 GTX 470 手写的 CUDA 内核，六个月工程量，课件评价「这个项目最后没有做成」 | **L357–491**：`Instructor's Story: First Deep Learning Project`、`Year 2010`、`One model variant`、`44k lines of code, including CUDA kernels for GTX 470`、`Six months of engineering effort`、`The project did not work out in the end.` | ✅ **五处逐字对应** |
| L92 那张按语言分行的表里「CUDA：21 个文件、7,871 行代码」 | **L404–412**：`CUDA / 21 / 1264 / 1042 / 7871`（列头为 `files / blank / comment / code`，见 L368–376）；该表 `SUM:` 的 code 列 = **44793**（L462–470） | ✅ **两个数字都对，而且取的是 code 列**（不是 blank/comment）——44,793 ≈ 「44k 行」也自洽 |
| L106/L108 对照：左边 44k 行 + 六个月，右边 `100 lines of python` + `A few hours`，靠 `System Abstractions` | **L497–569**：`44k lines of code`、`Six months` ↔ `Systems (ML Frameworks)`、`100 lines of python`、`System Abstractions`、`A few hours` | ✅ **逐字对应** |
| L112 「440 倍的落差」 | 44k ÷ 100 = 440（四则运算） | ✅ 算术对；**页面 L179 已声明这层因果是我们的归纳** ✅ |
| L116 引文 `A holistic approach (ML, Data, Systems, Hardware) to solve the problem of interest.` | **L656–663**：`A holistic approach (ML, Data, Systems, Hardware) to solve the problem of interest.` | ✅ 逐字对应 |
| L132 ML 改法：剪枝、蒸馏（把计算量压下来） | **L738–741**：`Design a better model with smaller amount of compute via pruning, distillation` | ✅ 逐字对应 |
| L134 系统改法：换更快的推理引擎（算子融合、内存复用、调度改进） | **L780–782**：`Build a better inference engine to reduce the latency and run more accurate models.` | ✅ 主体逐字对应；**括号里的三项技术是页面补的举例**（见 P1-1） |
| L136 ML 系统改法：收集更多数据 / 引入专用硬件 / 针对硬件设计模型结构 / 拼成端到端系统 | **L824–866**：`Collect more data` / `Incorporate specialized compute hardware` / `Develop models that optimizes for the specific hardware` / `Build end-to-end systems that makes use of the above points` | ✅ **四条逐项对应** |
| L138 三条路线的差别在「可改动的变量个数」 | 源无此说法 | ✅ 属页面自己的分析（L138 已用「可改动的变量个数」自陈是我们的判据；**建议纳入溯源，见 P1-1 同族**） |
| L140 MLSys 已是研究领域：NeurIPS 的 AI Systems workshop、系统/DB 会议的 MLSys 分轨、专门的 MLSys 会议（mlsys.org） | **L897–912**：`MLSys: The New Frontier of Machine Learning Systems`、`AI Systems Workshop at NeurIPS`、`MLSys tracks at Systems/DB conferences`、`Conference on Machine Learning and Systems (MLSys.org)` | ✅ **四条逐字对应** |
| L144/L148 `Why study machine learning and systems?` 三条理由 | **L921–941**：`Reason #1 To push the frontier of modern AI applications, we need to have a holistic approach…`、`Reason #2 Prepare ourselves to build machine learning systems and work in the area of machine learning engineering.`、`Reason #3 Have fun building our own ML systems!` | ✅ 三条逐字对应 |
| L152 学完之后应该能做什么（理解框架通用组成部分：自动微分/硬件加速/并行化/省内存；理解生成式 AI 的系统技术；自己实现一个项目） | **L1050–1074**：`understand the general components of modern machine learning frameworks, including concepts like automatic differentiation, hardware accelerations, parallelization and memory-saving techniques` / `understand systems techniques for emerging generative AI applications` / `implement your own machine learning systems project` | ✅ **三条逐字对应** |
| L160 课程四块组成 + 评分 45%/45%/10% + 期末项目 2–3 人一组 | **L1214–1250**：`This course will consist of four main elements`（`Class lectures` / `Programming-based (individual) assignments` / `(Group) final project` / `Interaction/discussion in piazza`）、`Grading breakdown: 45% assignments, 45% project, 10% class participation`；**L1266–1272**：`done in groups of 2-3 students` | ✅ **四块、三个百分比、分组规模全对** |
| L162 先修：系统编程、线性代数、一点数学基础、Python 与 C++；「这是一门偏系统的课…」 | **L1141–1205**：`Systems programming (e.g., 15-213)` / `Linear algebra (e.g., 21-240 or 21-241)` / `basic mathematical background (21-127 or 15-151)` / `Python and C++ development` / `Prior experience with machine learning or AI` / `This is a system-focused course, so make sure you are comfortable in system programming` | ✅ 逐条对应（源还列了 `Prior experience with machine learning or AI`，页面放在 L150「这门课预设你已经会一点机器学习」处 ✅ 未丢） |
| L164 「第三次开这门课、讲义正在翻新、内容和作业里几乎肯定有 bug」 | **L1019–1039**：`Big bold disclaimer / This is a third time offering of this course. We are revamping the materials to include latest advances in Machine Learning Systems.` / `The material and outline will likely adjust throughout the semester. There will almost certainly be some bugs in the content or assignments.` | ✅ 逐字对应 |
| L179 溯源里对「哪些是课件、哪些是我们的归纳」的声明 | — | ✅ 该声明与页面的实际写法一致（**除了 P1-1 列出的几处术语展开没有纳入**） |

---

## P1 · 易误解或依据不足

### P1-1 五处「术语/机制的展开」在课件里没有依据，也没有纳入页面的「属于 CourseLingo 讲解」声明

页面 L179 已经建立了一个很好的约定：
> 「数字与年份以课件页面为准；**课件没有展开的推论（例如「440 倍落差来自抽象层」「三根支柱之间不是加法」这类归纳），属于 CourseLingo 的讲解**，不当作原文引用。」

但有五处**同类的展开**没有进这个声明，而它们在 faithful 文本层里**找不到依据**：

| # | 位置 | 页面说 | 我检索过的词 | 源里实际有的 |
| --- | --- | --- | --- | --- |
| 1 | L52 | MTurk 的机制：`任何一个普通人做完一小块就结算一次，于是「雇一批人做几个月」变成了「按需买几万次点击」` | `MTurk` | 只有标签 `2004 … MTurk`（L189–192），无机制说明 |
| 2 | L54 | 张量核心「是 GPU 上专门做小矩阵乘加的电路，一次能干完过去好几条指令的活」；公有云「算力从自己买机器变成按小时租」 | `TensorCore` | 只有 `TensorCore`（L247）这一个词 |
| 3 | L98 | 「模型结构、内核实现、硬件调优三者互相绑住」 | `kernel`、`register`、`shared memory` | 源只有 `44k lines of code, including CUDA kernels for GTX 470`（L481–483）与 `Six months`（L486） |
| 4 | L110 | 「这层抽象具体包了五件事：把张量表示出来，把算子拼成计算图，沿着图自动求导，把图里的算子映射到具体内核，以及调度这些内核的并行执行」 | `tensor` / `computational graph` / `operator` / `schedul` / `automatic differentiation` / `parallelization` | 源里只有两个词能对上：学习目标页的 `automatic differentiation` 与 `parallelization`（L1058–1062）；**「张量表示 / 计算图 / 算子映射到内核 / 内核调度」四项在整份 faithful 文本里 0 命中** |
| 5 | L134 | 「算子融合、内存复用、调度改进」 | 同上 | 源只有 `Build a better inference engine to reduce the latency and run more accurate models.`（L780–782） |

**裁决**：**P1（依据不足，不是判错）**。这五处内容**都是业界准确的常识**，读者不会被带错；问题只在**出处**——
而这一页**恰恰已经建立了「哪些是课件、哪些是我们的话」的约定**，这五处漏在外面，会让读者以为它们是课件给的展开
（第 4 处尤其明显：它以一个「具体包了五件事」的枚举句式出现）。
**修在**（二选一，都是一句话的成本）：
① 把 L110 改成「按我们的归纳，这层抽象大致管五件事：…」，并在 L179 的声明里补上「术语的展开（MTurk 机制、张量核心、系统抽象包含什么、推理引擎的常见优化）」；
② 或把这五处逐条挂到源页（其中第 4 处的「自动微分／并行化」可以直接引学习目标页）。

**同族但我不判 P1 的一处**：L26「延迟预算来自物理：车速越高，留给检测与制动的时间越短」——这是对**动机**的常识性补全，
源里没有这句，但页面是在解释「为什么这个任务同时挂着两个数」，属于导语的合理的讲解，我记录在此供作者判断。

---

## P2 · 措辞

### P2-1 「2017 年**之后**的公有云」——课件上标的是 2017

正文 L54：「…与 **2017 年之后**的公有云」。faithful 文本里那一页的年份是 `2016`（TensorCore）与 `2017`（Public cloud），**没有「之后」的表述**。
⇒ 建议去掉「之后」，或改成「2017 年前后的公有云」。（**注意**：faithful 是纯文本，年份与名词的**版面绑定**我无法从这里唯一确定 —— 见下面「我核不到的」第 1 条。）

---

## 我核不到的（诚实记录）

> 按 `附录十四`：**「我没搜到」不等于「源材料没有」。** 下面是我**没有**找到依据的部分 ⇒ 我不能说它对或错。

1. **页 L54 里「2016 ↔ 张量核心」「2017 ↔ 公有云」的年份绑定**：faithful 那一页的文字顺序是
   `2016 → Compute → scaling → Public → cloud → TensorCore → 2017 → 2019`，**年份与名词谁配谁取决于版面**（PPT 的形状位置），
   纯文本层无法唯一确定。所以：**页面写的这组绑定与课件上的年份集合一致、但绑定关系我核不到**；P2-1 只针对「之后」这个措辞。
   检索范围：`mlsys-slide-01-course-introduction.pdf.faithful.txt` 全文；检索词 `2016|2017|TensorCore|Public|cloud`。
2. **本讲配图的视觉层**：我只核了 SVG 的文字与 `desc`/`title` 是否与正文、与源一致（11 张逐张比对，未发现数字冲突）；
   **几何（对齐/间距/墨迹）不在我的范围**（Lead 说该页配图已过视觉复核）。
3. **`text-clean/*.txt`**：按 Lead 的规则我**没有**使用它；因此我**没有**用第二份抽取产物交叉验证每一条（用的是 faithful + 原始 embedded 两处）。

---

## 覆盖面（附录十二）

- **已验**：时间轴 5 个年份与名称、2010 项目代码表（CUDA 21 文件 / 7871 行 code / SUM 44793）、AlexNet 三栏 8 个条目、
  100 行 vs 44k、三条理由、三条学习目标、课程四块组成 + 评分 45/45/10 + 分组 2–3 人、先修 5 项、翻新免责声明、
  以及 8 处逐字引用（`Many algorithms…before 2000`、`A holistic approach…`、`System Abstractions`、`100 lines of python`、
  `The project did not work out in the end.`、三条 Reason、学习目标三条、`This is a third time offering…`）。
  11 张配图的 `title`/`desc`/图内文字与正文逐张比对（未发现数字冲突）。
- **未验**：机检指标（`audit_content.py` 等）；配图几何；faithful 与 embedded 之外的第三份抽取；上面「我核不到的」1 条。

---

**核对人声明**：本记录只覆盖开头那个哈希的版本（`6CBE59318BBAF47B`）。按附录五，对其它版本的结论不成立。
本记录只读正文、不修改任何 `content/` 文件；`status` 由 Lead 处理。
