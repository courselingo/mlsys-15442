# 事实核对 · mlsys-15442 第 19 讲 机器学习编译进阶：把模型部署到云与端
- 核对人：非作者
- 核对日期：2026-09-29
- 被核对版本：content/19-advanced-ml-compilation/index.md，归一化 SHA256 前16 = `0EE0B0BC04E87D03`（全文 20,017 B）
- 源材料：`_sources/mlsys-15442/evidence/mlsys-slide-advanced-topic-mlc.pdf.faithful.txt`（45,156 B；含 **81 个 NUL 字节** ⇒ `read` 按二进制拒读，改用逐行读取）+ 同目录原件 `mlsys-slide-advanced-topic-mlc.pdf`（**目视渲染**，pypdfium2 5.13.0，scale=3）
- 抽取器与锚词（按说明第 ② 条先试探）：
  - 抽取器 = `.faithful.txt`（mlsys-15442 规定用这个）。
  - 锚词 `Relax` 13 命中 / `XGrammar` 3 / `IRModule` 3 / `vLLM` 3 / `Composable` 3 —— **锚词全部命中**，本文件**没有**出现 −0x1D/+0x1D 的逐字符错位，也没有 kern 把词切碎到不可检索（`Fine-tuned` 之类不存在于本 deck）。因此本讲**可以**下否定性结论，但下列否定性结论仍逐条写清检索词。
  - ⚠️ **「文本块数 ≠ PDF 页数」在本文件不成立的那一半**：本文件的 `===== PAGE =====` 分隔符正好 **57 个块、PDF 原件也是 57 页**（`pdfium.PdfDocument` 实测 `len(doc)=57`）。本记录仍**一律用「幻灯片标题 + 逐字原文」定位**，页号只作辅助。

## 结论
P0（事实错误）：**3** 条 ｜ P1（易误解/依据不足）：**2** 条 ｜ P2（措辞）：**3** 条

## P0 · 事实错误

| # | 位置 | 正文说 | 源材料说 | 依据（逐字引用 + 幻灯片标题） |
| --- | --- | --- | --- | --- |
| P0-1 | 正文「课件问：最大的挑战在哪」第 58 行；配图 `figures/advanced-ml-compilation-4.svg` 的「偏向模型一侧」块（第 23 行）与 `desc`（第 4 行） | 「偏向模型一侧的有**稀疏权重与参数分片**；偏向工程一侧的有内存、规划、算子库、派发与算子融合。」 | 标题 `What is the Biggest Challenge?` 的页面把清单排成**两行**：上排行标 `ML modeling`＝`Language Models` / `Diffusion` / `MultiQuery Attention` / `RoPE`；下排行标 `ML Engineering`＝`Memory Planning` / `Library Dispatch` / `Sparse Weights` / `Paged Attention` / 第二排 `Op Fusion` / `Parameter Sharding` / `Quantized Kernels` / `Layout Optimization`。**`Sparse Weights` 与 `Parameter Sharding` 两块都在 `ML Engineering` 行标之下**（不是模型侧）。 | 幻灯片标题 `What is the Biggest Challenge?`。faithful 文本层该页（4 个文本块之一）逐字为：`What is the Biggest Challenge? \| ML modeling \| ML Engineering \| Memory \| Planning \| Library \| Dispatch \| Op Fusion \| Parameter \| Sharding \| Sparse \| Weights \| Quantized \| Kernels \| Paged \| Attention \| Language \| Models \| Diffusion \| Layout \| Optimization \| MultiQuery \| Attention \| RoPE \| ML engineering now becomes critical and go hand in hand with ML modeling \| It is not about build silver bullet once but \| continuous improvement and innovations`。因文本层不保留坐标，**改用原件目视**（`pdfpage8.png`）：`Sparse Weights` 与 `Parameter Sharding` 两个徽章与 `Memory Planning`/`Library Dispatch`/`Paged Attention`/`Op Fusion`/`Quantized Kernels`/`Layout Optimization` 同处 `ML Engineering` 行标右侧，`ML modeling` 行标右侧只有 Language Models / Diffusion / MultiQuery Attention / RoPE 四块。 |
| P0-2 | 正文第 164 行配图说明：「**四个框**分别是智能体流程里的**四个环节**」 | 指向 `Agentic Flow` 链条上有**六个**主阶段。 | `Agentic Flow` 行逐字为：`context \| prefill \| thinking \| actions(call) \| ... \| thinking \| output`（`...` 表示中间还有重复阶段）。目视 `pdfpage36.png`：`context`（橙）、`prefill`（绿）、`thinking`（黄）、`actions(call)`（蓝框）、`…`、`thinking`、`output`——共 6 个实体框 + 1 个省略号。正文第 166 行自己写的也是「预填充、**上下文**、思考、动作调用、再输出」，即 5 个不同名称 ⇒ 与「四个环节」自相矛盾。 |
| P0-3 | 配图 `figures/advanced-ml-compilation-10.svg` 第 23 行（及 `desc` 第 4 行）：反量化的「计算模式是**逐元素的**」 | 案例页把该算子的 compute pattern 标注为 **`Injective`**，「逐元素」是另一回事。 | 幻灯片标题 `Case Study: Operator Fusion for Quantized Model`。聚合该页逐字原文：`func_attr("compute_pattern", "Injective")` … `func_attr("compute_pattern", "OutputEwiseFusible")`。源里出现的模式标签只有 `Injective`（`decode_q4`）与 `OutputEwiseFusible`（`mm`），**没有** `pointwise`/`逐元素` 这个标签。正文第 138 行写的「标注成单射」是对的 ⇒ 配图与正文不一致，且配图这一格是配图自身的事实主张。（`Injective` 与 elementwise 语义相关，但**标签名不是源里的词**。） |

## P1 · 易误解或依据不足

| # | 位置 | 正文说 | 问题 | 依据 |
| --- | --- | --- | --- | --- |
| P1-1 | 溯源第 215 行 | 「课件在这一讲里引了**两处**外部材料……**Relax**……**XGrammar**……课件还标注了 XGrammar 在 vLLM 里的集成以及一份来自 vLLM 博客的来源。」 | 计数少报，且**同一句话内部自相矛盾**（把 vLLM 博客说成「还标注了」= 第 3 处，却又把总数说成「两处」）。原件里可辨认的**带署名的外部材料共 3 处**。 | ① 标题页 `Relax: Composable Abstractions for End-to-End Dynamic Machine Learning`（幻灯片标题 `Relax: Composable Abstractions for End-to-End Dynamic Machine Learning`）；② `XGrammar: Efficient and Flexible Grammar Engine`（幻灯片标题同名）；③ 幻灯片标题 `XGrammar in vLLM` 下的 `Source: vllm blog` —— **目视 `pdfpage43.png` 确认该页整幅是第三方图表**（标题 `vLLM Guided Decoding Time per output token`，副标 `Llama-3.1-8B | H100 GPU | NousResearch/json-mode-eval | 50% guided decoding`，柱状图 `XGrammar`/`Outlines`），页脚 `Source: vllm blog`。此外幻灯片标题 `Low-latency Server GPU Serving` 页脚列为 `https://blog.mlc.ai/2024/10/10/optimizing-and-characterizing-high-throughput-low-latency-llm-inference` 并含两块署名第三方图（`Llama3 70B provider latency leaderboard` 带 `Artificial Analysis` 标与 `SGLang v0.3.1.post2, vLLM v0.6.1.post2` 字样）。正文第 215 行的「**均未转载其原图**」只对 Relax 与 XGrammar 两处成立，**对 vLLM 博客那一处不成立**。 |
| P1-2 | 正文第 60 行；配图 `…-4.svg` 第 28 行 | 「这组问题的共同点是它们都跨在『模型的意图』与『硬件的约束』之间」；配图：「这两侧的**边界**正是编译要处理的地方」。 | 源里**没有**「模型侧／工程侧」这个二分，也没有「两者交界处」这句话。该页给的两行行标是 `ML modeling` / `ML Engineering`，末句是 `ML engineering now becomes critical and go hand in hand with ML modeling`（并列与协作，不是「中间有一道边界」）。此二分与「交界」属 CourseLingo 的编排，但被摆在**陈述课文内容**的位置，且溯源第 217 行的「课件未展开的推论」清单里**没有登记**它。 | 见 P0-1 的逐字引用：`ML engineering now becomes critical and go hand in hand with ML modeling`。检索词：`boundary`、`border`、`interface`、`cross`、`between`、`modeling`、`engineering`（均在 faithful 全文）。 |
| P1-3 | 正文第 70 行、第 74 行 | 「课件认为**后一种正在变多**」「课件认为后者在变多」。 | 课件这一页（`Development Patterns in Age of LLMs`）列了三种开发方式并标注各自的性质（`Normal development assuming a mature framework foundation` / `Normal compiler development … Slow to change across multiple layers.` / `Domain specific ML compilation pipeline development … Customize both initial composition and transformation.`），**没有**任何一句说第三种/第二种「正在变多」。这是从课件对第三种方式的评价里读出来的判断。 | 幻灯片标题 `Development Patterns in Age of LLMs`。检索词：`more`、`increasing`、`growing`、`trend`、`becoming`、`popular`（均在 faithful 全文）；**逐字读完整 deck 57 页的聚合文本**后确认该判断无直接出处。 |

## P2 · 措辞

| # | 位置 | 正文/配图 | 说明 |
| --- | --- | --- | --- |
| P2-1 | `figures/advanced-ml-compilation-5.svg`（「两者交界」一格）；`…-8.svg`、`…-12.svg` 的 `desc` 用两格列举 | 配图把源的单页结构重塑成「交界／两格」 | 源 `Development Patterns in Age of LLMs` 是**三种**方式并列；配图只画「两种方式」，把第三种（域专用 ML 编译流水线）并进第二格。正文第 70 行确实只讲两种，但配图 `desc` 与源的一页不对应。属结构简化，不算事实错误，但读者按图索骥会漏掉一档。 |
| P2-2 | 正文第 96 行 | 「那个问号就是**未知的批大小**」 | 源只写 `unknown ?`，未把该维命名为 batch。这是从 `get_shape_value(x, axis=0)` 读出来的合理推断，但**不是**原文用词。 |
| P2-3 | 正文第 88 行；`figures/advanced-ml-compilation-6.svg` 第 26 行 | 正文「用**装饰器**标注，用类型标注写清输入的形状与数据类型」；配图「用装饰器标注张量运算」 | 源里 `@tvm.script.ir_module` 标在 **Module 类**上、`@R.function` 标在**函数**上，另有 `@tensorir_function` 标张量程序。正文与配图都没说清是哪个装饰器、标在什么上，容易被读成「装饰器标在矩阵乘函数上」。 |

## 我核不到的（诚实记录）

- **第 15 讲「TIRx 的动机」无法回源**。正文第 72 行称「第 15 讲讲 TIRx 的动机时，说的正是同一件事」。第 15 讲在本仓库的源是**网页版**（`https://mlsyscourse.org/slides/tirx-gemm/`，见 `content/15-blackwell-tirx/index.md` front matter），`_sources/mlsys-15442/evidence/` 下**没有**它对应的 PDF / faithful 文本。我在证据目录全部 20 个 `.faithful.txt` 里检索 `TIRx` —— **全部 0 命中**；检索 `(?i)tir` —— 亦 0 命中。⇒ 这是**抽取范围外**，我**不能**说这句对或错。（顺带记录：`evidence/` 里的 `mlsys-slide-15-LLM-serving-part2.pdf` 实为 repo 第 16 讲的源；`mlsys-slide-FlashInferCMU.pdf` 是 Zihao Ye 的 guest talk，与第 15 讲无关。**课件号与讲次号差两位在本课程成立**，见下。） |
- **正文第 72/74 行的因果串**「模型形态的变化速度快过框架的适配速度 ⇒ 第二种方式变多」：结论部分记在 P1-3；「变化速度快过适配速度」这一半我在课件里也找不到直接句子（检索词 `fast`、`speed`、`evolve`、`adapt`、`framework`），只找到评价性的 `Slow to change across multiple layers.`。作为「我们的解读」可以成立，作为「课件认为」不能。
- **正文第 50 行的组合数举例**（十种模型 × 十种设备 = 100 份 vs 20 份）是自撰算例，课件没有这组数；溯源第 217 行已把「工程量随目标数线性上涨」登记为因果推论，算例本身未见登记（不单列为条目，记在此处备查）。
- **`[[term:...]]` 词条**（`ml-framework`、`hardware-accelerator`、`kernel`、`compute`、`throughput`、`latency`、`computational-graph`、`end-to-end`、`machine-learning-system`）不在本讲页面正文的核对范围内，我未核对词条定义。
- **正文第 84 行「那个构造叫 IRModule，里面装着若干函数」**：源逐字为 `Centers around one key construct` + `A collection of (tensor) functions that correspond to model components.` —— 「若干函数」可以，但源补了一句「对应模型组件」，页面未提（不单列，备查）。

## 覆盖面

- **配图：14 张**（`advanced-ml-compilation-1.svg` … `-14.svg`，与正文 14 处 `![...]` 一一对应，无游离图）。
  - **逐张通读：6 张** —— `-2`（光谱）、`-3`（管什么/不管什么）、`-4`（两侧分类）、`-6`（Relax/IRModule）、`-7`（符号形状/问号）、`-12`（智能体四框）、`-14`（落地目标）；另**逐字读出 `desc` 与 `<text>` 节点**以核对说明文字（`desc` 不渲染，但它会被读屏与搜索碰到）。
  - **定向检索：0 张**（其余 8 张我只核对了正文中与它们绑定的数字/主张是否在源里有依据，未逐字通读其 `<text>`）。
  - 未逐张通读的 8 张：`-1`、`-5`、`-8`、`-9`、`-10`、`-11`、`-13`。**其中 `-10` 已因 P0-3 单独核过那一格**。
- **否定性结论的范围与检索词**（faithful 全文，逐行 UTF-8 解码 + NUL 替换）：
  - 「模型侧/工程侧二分」：`boundary` / `border` / `interface` / `cross` / `between` / `hand in hand` → 只有 `hand in hand` 命中（即 P1-2 引的那句）。
  - 「正在变多」：`more` / `increasing` / `growing` / `trend` / `becoming` / `popular`。
  - 「逐元素/pointwise」：`pointwise` / `ewise` → 只命中 `OutputEwiseFusible`；`element` / `elementwise` → 0。
  - 「两处外部材料」：`Source` / `blog` / `arxiv` / `http` / `citation` / `cite` / `Reference` → 命中点集中在 `Source: vllm blog`、`blog.mlc.ai/2024/10/10/...`、`huggingface.co/spaces/mlc-ai/WebLLM-JSON-Playground`、`https://webllm.mlc.ai/`。
- **原件目视**（pypdfium2 渲染，产物在**课程仓库之外**：`D:\Vibe_Workspace\_scratch_mlsys21\img\`）：第 8、36、43、49、6 页，共 5 页。P0-1 与 P1-1 的结论均由目视定案。
- 页码口径：本文件 `===== PAGE =====` 57 块 = PDF 57 页，**本讲两者一致**（与「15:0 / 16:761 / 17:263 / 18:120 个 NUL」那四份同批，但块数恰好没差）。

## 跨讲承诺（说明第 ⑩ 条）

**本讲对别人许的承诺：无。** 逐字检查正文与溯源，全部指路都是**回指**（第 1、2、8、14、15 讲），**没有**「第 N 讲会讲透 X」这类前指承诺。⇒ 不存在「指向第 22 讲之后、不可能兑现」的承诺。

**别人对本讲的承诺（本讲是否兑现）：**
- 第 8 讲溯源第 209–220 行给出**全表**，其中含：`第 19 讲 ← advanced-topic-mlc（无编号）`、`第 20 讲 ← 18-kernel-superoptimization`、`第 21 讲 ← 19-mega-kernel`，并声明「本页以及全课程的其他页，一律用仓库讲次号指路」。
  - **第 19 讲已兑现**：本页溯源第 213 行逐字为「原文课件：https://mlsyscourse.org/slides/advanced-topic-mlc.pdf（课件号的对照见第 8 讲溯源；本页一律用仓库讲次号指路。）」—— **第 8 讲 ↔ 第 19 讲的双向对得上**（第 8 讲既列了本讲的课件映射，本页也回指了第 8 讲的那张表）。
- 第 2 讲曾对「换出/offload」许过承诺（第 11 讲核对者已证明其从未兑现）。**本讲与「换出」无关**：本讲源 57 页里 `offload` / `swap` / `pinned` / `host` **命中 0**（`cpu` 命中 1 次，为 `Mask generation on CPU cannot keep up`，讲的是掩码生成的位置，不是参数换出）。⇒ 本讲**没有**补上那个缺口，也**没有**对「换出」许下新承诺。

## 一处给 Lead 的备注（不属于本讲核对的结论）

`_sources/mlsys-15442/evidence/` 里的 `mlsys-slide-15-LLM-serving-part2.pdf` 与 repo 第 16 讲对应，而 repo **第 15 讲是网页版（tirx-gemm）不在证据目录里**。任何以本目录为唯一证据的核对，都**无法**核对第 15 讲，也无法核对任何「第 15 讲讲过 X」的跨讲主张——本讲的 P1-3/「核不到」项就是实例。
