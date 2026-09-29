# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 9 讲 并行化（上）：数据并行与零冗余优化

- 核对人：**非作者**（本讲任何一轮写作我都没有参与，也没有与作者 `mlsys-author` 讨论过本讲内容）
- 核对日期：2026-09-29
- 被核对版本：`content/09-ml-parallelization-1/index.md`
  归一化 SHA256 前16 = **0F7EFD48BE086A75**
  （全 64 位 `0F7EFD48BE086A753C5134CD94F12716E089C7B81628B56E415455FC27534957`，**19,568 B**；
  文件本身已是 LF（`\r\n` 计数 0），归一化后长度与哈希都不变；最后写入 2026-09-29 10:40:02）
  - 14 张配图（`figures/ml-parallelization-1-1.svg` … `-14.svg`）
- 源材料（本次实际依据的，逐个列出，并说明我怎么用它）：

| # | 文件 | 用途 / 说明 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-08-ML-parallelization-part1.pdf`（**4,001,089 B**） | 权威源。**取件校验**：尾部 `\r\n4000900\r\n%%EOF`（`startxref` 指向 4,000,900 < 4,001,089）、大小**不是** 2 的整数次幂 ⇒ 判定为完整件；对象层 `/Type /Page` 78 个、`/MediaBox` 78 个、`/Pages` 1 个、`/Count 78` |
| 2 | 同目录 `.faithful.txt`（**43,493 B**，380 个 NUL，78 个 `===== PAGE =====` ⇒ **79 个文本块**） | **主要依据**（按项目约定用 faithful）。我为阅读做了去 NUL/控制字符的只读副本（`%TEMP%`，未改源文件）。按「幻灯片标题 + 逐字原文 + 文本块序号」定位，**行号不作坐标** |
| 3 | 同目录 `.embedded.txt`、`_sources/mlsys-15442/text-clean/*.txt` | **一律未使用**（按规则：前者是字体二进制，后者会把 kern 分段留成词内碎片） |
| 4 | `evidence/mlsys-site-lectures.yml`、`evidence/mlsys-course-schedule.html` | 核本讲的**周次、日期、讲者**（两个独立取件互证） |
| 5 | `evidence/mlsys-slide-09-ML-parallelization-part2.pdf.faithful.txt`（21,096 B）与同目录 part2 PDF（2,985,543 B，`%%EOF`，`/Count 34`） | **专项**：核第 9/10 两讲是否重叠、有没有引用对方范围 |
| 6 | `glossary.toml` | 核本页 8 个不同的 `[[term:…]]` |
| 7 | `evidence/mlsys-webrepo-LICENSE.bin`（**正好 19,342 B**） | 核溯源 L216 的许可体积 |

> **定位约定（重要）**：faithful 分出 **79 个文本块**，而 PDF 对象层是 **78 页**（`/Count 78`）。
> 两者差 1，我在本环境里**没有 PDF 解析库**（无 pypdf/PyPDF2/pdfminer），**没有解开这个差**。
> ⇒ 所以本记录一律用「**B\<n\>**＝faithful 第 n 个文本块 + 该页幻灯片标题 + 逐字原文」定位，
> **不写「pN = PDF 第 N 页」**（第 11 讲那一份两个口径都是 28，见第 11 讲记录）。

> **文本层可用性（锚词试验，按说明文件三步走）**：这份 faithful 的正文**没有** eth-ca 那种按页静默错位。
> 我用的锚词与命中：`AllReduce`（119 处命中）、`Best latency`（1）、`Progressive memory`（3）、
> `0.32B`/`1.5B`/`17.2B`/`175B`/`5.12GB`/`2800GB`/`12288`/`547x`（各 2）、`2M bytes`（2）、
> `16M bytes`（1）、`20GB/GPU`（1）、`NVIDIA V100`（1）。
> 损坏只出现在**公式与图形标注**那段字形码里（例如 B25 的 `t H 0 H / 0 6 H / t H 0 H…`、B6 的 `S Ü S Ü F Û Ï`）。

---

## 结论

**P0（事实错误）：4 条 ｜ P1（易误解/依据不足）：3 条 ｜ P2（措辞）：4 条**

四条 P0 里，**两条是「否定性结论／计数体系」这一类**（说明文件方法 ② 与 ⑧ 点名的那两类），
一条是**周次归属**，一条是**方向写反**（方法 ④ 点名的那类：`树形在工人数少时更省`）。
这一讲的数字（N(N−1)M / 2M / 2NM / NM·logN）我**逐个回源核过**，四个公式**都对**；
出错的是那句把两套计数体系并排比较的话（P0-3）。

---

## P0 · 事实错误

### P0-1 L8 / L13 / L214 把 2026-02-11 这一讲记成「Week 6 / 第六教学周」——课程表写的是 **Week 5**

| # | 位置 | 正文说 | 源材料说 | 依据（逐字引用） |
| --- | --- | --- | --- | --- |
| 1 | L8（front matter `source_title`）、L13、L214 | `Week 6: Parallelization Part 1 (Data Parallelism and Zero Redundancy)（Zhihao Jia 主讲，2026-02-11）`；L13 还多写一句「**第六教学周**」 | 2026-02-11 那一讲属于 **Week 5** | `mlsys-course-schedule.html`：`02/11 Wed` → `Week 5: ML Parallelization (Data Parallelism and Zero Redundancy) [ slides ] Zhihao Jia Lab 1 Due`；`mlsys-site-lectures.yml` L82-89：`- date: 02/11 Wed / lecturer: Zhihao Jia / title: Week 5: <strong>ML Parallelization (Data Parallelism and Zero Redundancy)</strong> / slides: /slides/08-ML-parallelization-part1.pdf` |

- 两个**独立取件**（一份 yml、一份 html）都写 Week 5；前后两条也对得上：`02/09 Mon` 是 `Week 5: Case study: Transformer…`，`02/16 Mon` 是 `Week 6: ML Parallelization (Model and Pipeline Parallelism)`。
- 用日历也能自证：第一周从 `01/12 Mon` 起算 ⇒ `01/12`=W1、`01/19`=W2、`01/26`=W3、`02/02`=W4、`02/09`=**W5**，`02/11` 落在 W5。
- **课件自己没有印周次**（B1 标题页只有 `15-442/15-642: Machine Learning Systems / Parallelization Part 1 (Data Parallelism and Zero Redundancy) / Tianqi Chen and Zhihao Jia / Carnegie Mellon University / 1 / 2/11/2026`）。
  ⇒ 所以「Week 6」不是课件里的字，而是我们这一页替课件加的**归属**；既然加了，就要按本课程的课程表加。
  如果这 3 处是从**别的开课年份**（那时并行化排在 Week 6）搬来的，请在溯源里写清是哪一个年份，否则读者会把它当 2026 春的课表。
- 「Zhihao Jia 主讲」这一半**是对的**（课程表 `lecturer: Zhihao Jia` ✅），日期 `2026-02-11` 也**是对的** ✅ —— 错的只是周次。

### P0-2 溯源 L219 说那页大模型对照表「文字层里没有可直接引用的具体数值」——数值就在文字层里，逐字可检索

- **正文 L219 逐字**：「课件在那张大模型参数量的对照页上给的是图形化的柱状对比，**文字层里只留下 Bert-Large、GPT-2、Turing 17.2 NLG、GPT-3 这几个名字，没有可直接引用的具体数值**，所以本页只写趋势、不写数字。」
- **源（B28 / B29，两份几乎相同的帧，标题都是 `Large Model Training Challenges`）逐字**：
  ```
  Bert-Large   GPT-2   Turing 17.2 NLG   GPT-3
  Parameters          0.32B   1.5B   17.2B   175B
  Layers              24      48     78      96
  Hidden Dimension    1024    1600   4256    12288
  Relative Computation 1x     4.7x   54x     547x
  Memory Footprint    5.12GB  24GB   275GB   2800GB
  ```
  第二份帧（B29）还多两行：`NVIDIA V100 GPU memory capacity: 16G/32G`、`NVIDIA A100 GPU memory capacity: 40G/80G`、`Out of Memory`。
- 同一份 faithful 里这些串的命中次数：`0.32B`=2、`1.5B`=2、`17.2B`=4、`175B`=2、`12288`=2、`547x`=2、`5.12GB`=2、`2800GB`=2 ⇒ **不是我读错，也不是字形码**。
- 相关的一页也有硬数字（B39，标题 `Understanding Memory Consumption`，`M = number of parameters in the model`）：
  `FP16 parameter: 2M bytes`、`FP16 Gradients: 2M bytes`、`FP32 Optimizer States: 16M bytes`、
  `Gradients, Variance, Momentum, Parameters`、`Example 1B parameter model - > 20GB/GPU`、`Memory consumption doesn't include Input batch + activations`。
- 这条之所以记 P0，是因为它**不只是漏写**：它以「源里没有」为理由，替读者关掉了一整页可引用的数字
  （说明文件第 ⑨ 条的镜像：**少认了源材料**）。修法是把四组数字补进正文/配图，或者把理由改成「本页选择只写趋势」。

### P0-3 L138「环形那两项里没有 N」——课件给环形的两项正是 `M * N`

- **正文 L138 逐字**：「课件把参数服务器、朴素 AllReduce、环形、树形四种放在一页上比较。把它们的通信量**并排**写出来，差别一眼可见：朴素那一项带着 N 的平方，树形带着 N，**而环形那两项里没有 N**。」
- **源（四个 Overall communication，逐字）**：
  ```
  B12 Naïve AllReduce      : Overall communication: N * (N - 1) * M parameters
  B19 Ring AllReduce       : Overall communication: 2 * M * N parameters
                             Aggregation: M * N parameters
                             Broadcast:   M * N parameters
  B21 Tree AllReduce       : Overall communication: 2 * N * M parameters
                             Aggregation: M * N parameters
                             Broadcast:   M * N parameters
  B23 Butterfly AllReduce  : Overall communication: N * M * log(N) parameters
  ```
  ⇒ 环形的**两项**（Aggregation / Broadcast）各是 `M * N`，**两项都带 N**；环形的 Overall 是 `2 * M * N`，也带 N。
- **这是两套计数体系被并排用了**（说明文件第 ⑧ 条）：课件 B25（标题 `Ring AllReduce v.s. Tree AllReduce v.s. Parameter Server`）里那句
  `More scalable since each worker sends 2*M parameters (independent to the number of workers)` 是**每个工人**的量（2M，与 N 无关）；
  而 `Overall communication` 是**全体合计**的量（`2*M*N`）。正文把「每工人的 2M」当成「环形的通信量」去和「朴素 N(N−1)M、树形 2NM」并排比大小 —— 单位不同，结论就反了。
- 值得肯定的是：本页 L114 与「读完应该能回答」第 4 题都**明确写了「每个工人的收发量…总共大约 2M」**，L208 也把树形的 `2NM` 标成「**整体**通信量」——两套体系本页都有，只是 L138 那一句把单位混掉了。配图 `-10.svg` 在这一点上比正文**更严谨**（它写的是「环形：**每个工人**约 2M」）。
- 建议改法：L138 改成「同一口径下：朴素 N(N−1)M、环形 2MN、树形 2NM 都是**全体合计**，其中朴素带 N²、其余带 N；换成**每工人**口径后，环形的 2M 才与 N 无关」。

### P0-4 L130 与配图 `-10.svg`「工人数少的时候树形更省」——课件给的两个延迟式与那句 `Best latency` 说的是相反方向

- **正文 L130 逐字**：「它和环形做法的差别在于「轮数」与「每轮数据量」的取舍。树形的轮数是 log N，比环形的 N 小得多，但每一轮要传的是完整的 M 个参数，而不是 M/N 片。**工人数少的时候树形更省**，工人数多、带宽又紧张的时候，环形那套「小片多轮」通常更稳。」
- **源（B25，标题 `Ring AllReduce v.s. Tree AllReduce v.s. Parameter Server`）逐字**：
  ```
  Each worker sends M/N parameters per iteration; repeat for 2*N iterations
  Latency: M/N * (2*N) / bandwidth            <- Ring
  Each worker sends M parameters per iteration; repeat for 2*log(N) iterations
  Latency: M * 2 * log(N) / bandwidth         <- Tree
  All workers send M parameters to parameter servers and receive M parameters from servers
  Latency: M * N / bandwidth                  <- Parameter Server
  Ring AllReduce:
    Best latency
    Balanced workload across workers
    More scalable since each worker sends 2*M parameters (independent to the number of workers)
  ```
- 按课件自己的式子：环形 `= 2M / 带宽`，树形 `= 2M·log N / 带宽` ⇒ **log N ≥ 1 时（N ≥ 2）树形永不更省，N = 2 时两者相等**。课件在 B24 还把这写成一道设问：
  `Question: Ring AllReduce is more efficient and scalable then Tree AllReduce and Parameter Server, why?`（原文 `then`）。
- ⇒ 「工人数少的时候树形更省」与课件的两个式子、`Best latency`、那道设问**三处都不一致**。这一句在溯源 L218 里被登记为「我们的取舍判断」，
  但它不是措辞松紧的问题，而是**方向问题**（说明文件方法 ④）；建议删掉，或改成课件支持的表述（环形的每工人量 2M 与 N 无关 ⇒ 更可扩展；树形每轮传整个 M，轮数只有 log N）。

---

## P1 · 易误解或依据不足

### P1-1 计数体系：正文 L88「三种做法」/ L138「四种放在一页上比较」/ 溯源 L217「四种做法…四者对比」——课件是**四种 AllReduce + 参数服务器共五列**

| 位置 | 正文说 | 源材料说 |
| --- | --- | --- |
| L88 | 「课件接着给了**三种做法**，一种比一种好」（随后讲了朴素、环形、树形） | B11（标题 `Different Ways to Perform AllReduce`）逐字列四项：`Naïve AllReduce`、`Ring AllReduce`、`Tree AllReduce`、`Butterfly AllReduce` |
| L138 | 「课件把参数服务器、朴素 AllReduce、环形、树形**四种**放在一页上比较」 | B24（标题 `Comparing different AllReduce Methods`）的列是五项：`Parameter Server`、`Naïve AllReduce`、`Ring AllReduce`、`Tree AllReduce`、`Butterfly AllReduce` |
| L217 | 「AllReduce 的**四种做法**：定义、朴素做法的 N(N−1)M、环形…、树形…、蝶形网络的变体，以及课件那一页的**四者对比**」 | 「四种做法」后面**枚举了 5 项**（定义／朴素／环形／树形／蝶形），其中「定义」不是做法；比较页是**五列** |

- 这是本页唯一一处**页内自相矛盾**：L132 自己说「课件**还提了**一种蝶形网络的变体」，说明作者知道蝶形存在，但 L88/L138 的计数把它排除在外。
- 溯源那一句里「四种做法」与随后 5 个枚举项打架，属于说明文件第 ⑧ 条「两套并存的计数体系，只说到了一套」。建议：正文统一成「四种 AllReduce 做法」，比较页写成「参数服务器 + 四种 AllReduce 共五列」。

### P1-2 L142 把 `latency` 的「含义」重新定义成「一轮里有多少次等对方」——课件那一页的 `Latency` 就是「通信量 ÷ 带宽」

- **正文 L142 逐字**：「[[term:latency]] 在这里的含义也变了：**不是单次传输要多久**，而是一轮 AllReduce 里有多少次「等对方」。轮数越多，等待的层数越多…」
- **源（B25）逐字**：`Latency: M/N * (2*N) / bandwidth`、`Latency: M * 2 * log(N) / bandwidth`、`Latency: M * N / bandwidth`
  ⇒ 课件这一页的 `Latency` **正是「要传的总量 ÷ 带宽」**（单次传输时间），课件也正是用这两个式子的**大小**得出 `Best latency`。
- 这不是把源的话讲错，而是**在同一页里给同一个词换了一个新含义**，读者很可能把后半句当成课件的结论。溯源 L218 已把它登记为「我们的推论」，
  所以在纪律上没错；但它与课件同页的用法相冲，建议写成「课件用「总量 ÷ 带宽」算延迟（环形 2M/带宽 最小）；**另外**，实际系统还要看一轮里等了多少次」。

### P1-3 溯源 L218 把三件**课件里有直接依据**的事登记成「我们的推论」（第 ⑨ 条的镜像：少认了源材料）

溯源 L218 逐字：「课件未展开的推论属于 CourseLingo 的讲解…一组是取舍判断：**环形与树形之间怎么选**、通信量小不等于更快、**延迟可以理解成一轮里有多少次等待**、第三阶段的代价与收益就是在显存与通信之间挪边界。一组是因果与量级：显存这道墙加卡绕不过去、**优化器状态往往是占比最大的一项**。」

| 被登记为「我们的推论」 | 课件里其实有直接依据 |
| --- | --- |
| 「环形与树形之间怎么选」 | B25 三个 `Latency:` 式子 + 逐字 `Ring AllReduce: Best latency` / `Balanced workload across workers` / `More scalable since each worker sends 2*M parameters (independent to the number of workers)` |
| 「优化器状态往往是占比最大的一项」 | B39 逐字 `FP16 parameter: 2M bytes`、`FP16 Gradients: 2M bytes`、`FP32 Optimizer States: 16M bytes`（16/20 = 80%，是四项里最大的一项） |
| 「第三阶段的代价与收益就是在显存与通信之间挪边界」 | B65 / B72 / B78 三处逐字 `Progressive memory savings and communication volume`（Stage 1 / Stage 2 / Stage 3） |
| 「延迟可以理解成一轮里有多少次等待」 | 这条确实是我们的提法（见 P1-2）——登记是对的 |

- 方向是**保守**的那一侧（把源的说法算到自己头上），所以危害小于「归属写反」；但说明文件第 ⑨ 条要的正是这个方向的自查：
  **在把一句话标成「我们补的」之前，先搜一遍源里有没有它**。这四项里前三项有源，建议改成引用 + 页码/标题。
- 顺带：这三处也正是 P0-2 / P0-3 / P0-4 同一批材料（B25、B39）——把 B25 与 B39 认真读一遍，能同时修掉 3 条 P0/P1。

---

## P2 · 措辞

| # | 位置 | 正文 | 源 | 说明 |
| --- | --- | --- | --- | --- |
| P2-1 | L132 | 「课件还提了一种蝶形网络的**变体**」 | B11 把蝶形与朴素/环形/树形并列成四种做法之一 | 「变体」把它降级了；与 P1-1 同源 |
| P2-2 | L164 | 「…然后是优化器状态，**混合精度下还会多一份 FP32 的参数副本**」（暗示 FP32 参数是优化器状态之外的另一项） | B38/B39 把 `FP32 Parameters` 归在 `FP32 Optimizer States: 16M bytes` 这一项里，逐字 `Gradients, Variance, Momentum, Parameters` | 16M 这一格里**已经含** FP32 参数副本；写成「优化器状态里含 FP32 参数副本、动量与方差」更贴源 |
| P2-3 | L62 / L64 | 「参数服务器用一个点消掉了这种不一致，代价是所有人都要排队等它」等异步训练一致性的论述 | 课件 B8（`Data Parallelism: Parameter Server`）只有那一句推拉描述与 B9 的中心化批评，**没有**异步/陈旧梯度那段 | 溯源 L218 的三组推论里**没有**登记这两段（登记的三组是取舍判断/因果与量级/分工的区分）；建议补登记 |
| P2-4 | 溯源 L214-L219 全篇 | 取材范围写得很细（四块内容逐项列出） | — | 但**通篇没有一个幻灯片标题或页码**，「Bert-Large 到 GPT-3 的参数量趋势」这类描述读者无法回源定位；建议每块后面缀一个课件标题（本页引用的四页标为 `DNN Training Process`、`Data Parallelism: Parameter Server`、`Different Ways to Perform AllReduce`、`ZeRO: Zero Redundancy Optimizer`、`Understanding Memory Consumption`、`Large Model Training Challenges`） |

---

## 跨讲承诺（说明文件第 ⑩ 条）

- **本讲作出的、带讲次编号的承诺：0 条。**
  L28 只写「后面几讲会把它继续展开」、L142 写「这个权衡在后面的分布式训练系统里会反复出现」，都**没有给讲次编号**，所以没有可回核的承诺清单。
- **本讲兑现了别人对它的承诺 ✅（但本页没有登记）**：`content/02-introduction-to-mlsys/index.md` 的溯源里逐字登记着
  「**第 9、10 讲：分别展开数据并行与模型并行**」。本讲确实是数据并行那一半（切数据、参数服务器、AllReduce、ZeRO），**兑现了**；
  但本页溯源里**没有**「已兑现第 2 讲承诺」这一行（L218 只写「本讲与前后讲次的对应关系属于我们的编排」）。
  建议按第 2 讲那种「跨讲承诺登记」的写法补一行，方便下一讲核对。
- 第 2 讲还登记了「**第 11 讲**：展开显存的两种省法（重算与换出）」——那是第 11 讲要回核的对象，见第 11 讲记录。

## 专项：第 9 / 10 两讲是否重叠（Lead 点名）

两讲是**两份独立 PDF**（各 1 份 `.faithful.txt`、各自的标题页页脚都是 `1`），页码各自从 1 起，这一点确认 ✅。

我做的检查：把 79 个文本块与 39 个文本块各自转成 4-gram 词元集合，逐块做 Jaccard。**除去页眉页脚模板**（`Automated Approaches to Accelerate Machine Learning` 之类，单独看会给 1.000 的假阳性），结论是：

| 第 10 讲的块 | 第 9 讲的块 | Jaccard（4-gram） | 判断 |
| --- | --- | --- | --- |
| deck09 B2（`Recap: Data Parallelism`） | deck08 B7（`Data Parallelism`） | **1.000**（共享 11/11） | **整页重复**，只有标题多了 `Recap: ` |
| deck09 B3（`Recap: An Issue with Data Parallelism`） | deck08 B26（`An Issue with Data Parallelism`） | **0.929**（共享 13） | **整页重复**，差的就是标题的 `Recap: ` |
| deck09 B18（`Example: Parallelizing Transformers`） | deck08 B33（`Transformer for Language Models`） | 0.714（共享 10） | 复用**同一张 Transformer 编解码图**（两页都有 `Encoder`/`Decoder`/`Ashish Vaswani et. al. Attention is all you need.`） |

- ⇒ 「两讲不重叠」这个说法要加限定：**正文主题确实不重叠**（第 9 讲＝数据并行 + AllReduce + 显存构成 + ZeRO；第 10 讲＝模型/张量/流水线并行），
  但第 10 讲开头**有 2 页是第 9 讲原页的逐字复制**（并在标题里以 `Recap:` 标明是回顾，**这个标法是对的**），另有 1 页复用第 9 讲的图。
- 「有没有引用对方范围却没标出处」：**第 9 讲这一侧未发现**（本页没有引用第 10 讲的任何内容；L28 的「后面几讲」没有指名）。
  反向（第 10 讲引用第 9 讲）在那一讲的记录里核；初步看它用的是「上一讲」并逐处标注 ✅。
- 给下一轮核对方的提醒：**别用页码互换**——两份 PDF 的页码各自从 1 起，且第 9 讲那一份 faithful 的文本块数（79）比 PDF 页数（78）多 1。

## 配图（覆盖面：逐张通读 14 张，定向检索 0 张）

- **逐张通读 14 张**：我把每张 SVG 的 `<text>` 节点全部读出来（含 `desc`/`title` 元数据，因为 `desc` 不渲染、只有通读才会碰到），14 张的可见文字互不相同。
- **有没有两张「可用文字几乎相同」（Lead 点名的 P1 判据）**：**没有**。两两比较的最高 Jaccard 是 **0.059**，共享的只有 1 个串（`N × (N − 1) × M`，出现在 `-7.svg` 与 `-10.svg`）。
  ⇒ 这 14 张不构成「同一骨架复用导致指纹去重」的问题。
- **「6 种不同版面」这句我实测了**：按每张 SVG 的 `<rect>` 的 y 坐标分带（每 10 单位取整）去重，**恰好得到 6 种**：
  `(10,70,170)`（1.svg、4.svg）、`(10,70,170,260)`（5.svg、11.svg）、`(10,70,140,230)`（**3/6/7/8/10/12/13.svg 共 7 张**）、
  `(10,70,140,230,320)`（9.svg）、`(10,70,160,260,350)`（2.svg）、`(10,70,170,250,340)`（14.svg）。
  ⇒ 作者自陈的「6 种版面」**对得上**；同时也要看到「7 张共用同一组 y 分带」这件事（但它们的文字与 rect 数都不同，所以不是同一张图）。
- 配图里与源冲突的地方：**只有 `-10.svg` 的 META 一句**「课件把参数服务器、朴素、环形、树形四种放在一页上比较」（同上 P1-1）与它的数字口径（同上 P0-3/P0-4）；
  其余 13 张的每一句话我都对回了源（例如 `-14.svg` 的「普通数据并行里所有 GPU 全程都留着全部参数」= B73 逐字 `In data parallel training, all GPUs keep all parameters during training`）。

## 我核不到的（诚实记录）

1. **faithful 的 79 个文本块 vs PDF 的 78 页**：对象层 `/Type /Page` = 78、`/MediaBox` = 78、`/Pages` = 1、`/Count 78`；faithful 是 78 个分隔符 ⇒ 79 块，且**没有空块**。
   我查过：`\x0c` 计数 0（这一份没有换页符）、没有 `===CURLMETA===` 尾巴、相邻块没有整页重复（重复的都是**动画帧**，各自是一页，例如 B3/B4/B5 的 `DNN Training Process` 页脚依次是 4/5/6）。
   本环境**没有 PDF 解析库**（pypdf / PyPDF2 / pdfminer 都未安装），所以我**没有**解开这 1 块的差，也**没有**用页码定位（改用了文本块序号 + 标题 + 逐字原文）。
2. **B24（`Comparing different AllReduce Methods`）比较表的每列数值读不出来**：那一页的值在文字层里是字形码（`t H 0 H / 0 6 H / t H 0 H…`）。
   ⇒ 我**没有**据这一页下任何结论，四个公式一律取自 B12/B19/B21/B23 各自的 `Overall communication:` 行。表格里那个 `Overall communicatio n`（原文断词）我照原样引。
3. **L20/L28「前面几讲都在一块卡上」「这一讲也是这门课第一次正面处理『多机』」**：这需要第 1–8 讲的课件才能核，我只核了课程表顺序（`01/12`…`02/09` 都是单卡/Transformer 主题）与第 2 讲页面的说法，**没有**逐份读前八讲的课件 ⇒ 不判对错。
4. **`Turing 17.2 NLG` 这个名字**：课件 B28/B29 逐字就是 `Turing 17.2 NLG`（本页照抄 ✅），但课件另一处（B65/B72/B78）写的是 `Turning NLR 17.2B`；哪个是官方写法我**没有**外部源可核（本轮只用缓存源，未联网）。
5. **L102 那段「比值一旦超过 1，加卡就是负收益」**：这是本页自己的量纲推理（`B/W/C`），课件没有这个式子，我按「我们的推论」处理，**不当事实错误**，也没有替它找源。
6. 我检索过但**确实没有**出现的写法（用于交叉验证不是「我没搜到」）：`Activation`/`checkpoint`/`bfloat16`/`float16`/`reduce_scatter`/`allgather`/`FSDP` **在本讲 faithful 里 0 命中**
   ⇒ 本讲**没有**讲激活检查点、混合精度的两种格式、`reduce_scatter + allgather`、FSDP 等价 ZeRO3 —— 那些是第 11 讲那一份课件的内容（第 11 讲记录里逐个回源）。

## 已逐条回源、未发现问题的（供作者放心，不重复计 P）

- 三个阶段的定义：B3/B4/B5 逐字 `1. Forward propagation: apply model to a batch of input samples and run calculation through operators to produce a prediction`
  `2. Backward propagation: run the model in reverse to produce a gradient for each trainable weight`
  `3. Weight update: use the gradients to update model weights`；L36 的三句中文与其**一一对应** ✅（注意 B3 那帧写的是 `produce error`、B4/B5 改成 `produce a gradient`——本页用的是后者，是对的 ✅）。
- 参数服务器原话：B8 逐字 `Workers push gradients to parameter servers and pull updated parameters back`；L60 的中文引与原话**逐字一致** ✅（配图 `-4.svg` 的简写 `push gradients` / `pull parameters back` 也 ✅）。
- 中心化批评与那句设问：B9/B10 逐字 `Centralized communication: all workers communicate with parameter servers for weights update; cannot scale to large numbers of workers` +
  `How can we decentralize communication in DNN training?`；配图 `-5.svg` 的「后果一/后果二」与 L74 都对得上 ✅。
- AllReduce 的定义：B10 逐字 `AllReduce: perform element-wise reduction across multiple devices`；L84 ✅；配图 `-6.svg` 的「归约之后，每台设备上都有一份完整的和」与 B10 的 `AllReduce` 合起来 ✅。
- 朴素做法：B12 的 `N * (N - 1) * M parameters` 与 L98 的中文「N 乘 N 减 1 再乘 M」✅；L100「8 加到 16 ⇒ 涨了大约 4 倍」我算过：`8·7=56 → 16·15=240`，**4.29 倍** ✅。
- 环形两步：B13/B14/B15（`Step 1 (Aggregation): each worker send one slice (M/N parameters) to the next worker on the ring; repeat N times`）、
  B17（`After step 1, each worker has the aggregated version of M/N parameters`）、B19（`Step 2 (Broadcast): each worker send one slice of aggregated parameters to the next worker; repeat N times`）；
  L110/L112/L114/L116 逐句对得上 ✅，且「每个工人约 2M、与 N 无关」= B25 逐字 `each worker sends 2*M parameters (independent to the number of workers)` ✅。
- 树形：B21 的 `repeat log(N) times` ×2 与 `Overall communication: 2 * N * M parameters`；L124/L126/L128 ✅（「树高 log N」与「走 log N 条边」自洽 ✅）。
- 蝶形：B23 逐字 `Repeat log(N) times: 1. Each worker sends M parameters to its target node in the butterfly network 2. Each worker aggregates gradients locally`
  + `Overall communication: N * M * log(N) parameters`；L132 ✅（`NM log N` 与 L128 的树形 `2NM` 是两个不同的量，本页没有混 ✅）。
- 显存构成与 Adam：B38 标签 `FP16 parameter` / `FP16 Gradients` / `FP32 Optimizer States` / `Gradients, Variance, Momentum, Parameters`；
  B39 的 `2M bytes` / `2M bytes` / `16M bytes`；L164/L166/L170 与之 ✅（一阶动量 + 二阶方差各一份、和参数同量级 ✅）。
- ZeRO 定位与阶段：B30 逐字 `ZeRO: Zero Redundancy Optimizer / Eliminating data redundancy in data parallel training / A widely used technique for data parallel training of large models`；
  B40 逐字 `ZeRO removes the redundancy across data parallel process / Stage 1: partitioning optimizer states / Stage 2: partitioning gradients / Stage 3: partitioning parameters`；
  L180/L182 ✅。阶段 2 的细节（`Partitioning gradients across GPUs`、`The forward process remains the same as stage 1`、`Perform AllReduce right after back propagation of each layer`、`Only one GPU keeps the gradients after AllReduce`、`Reduce gradients on GPUs responsible for updating parameters`，B66-B71）本页未展开但**没有写错** ✅。
- 第三阶段：B73 `In ZeRO, model parameters are partitioned across GPUs`、B74 `GPUs broadcast their parameters during forward`、B75 `Parameters are discarded right after use`、B76 `GPUs broadcast their parameters again during backward`；
  L192/L194/L196 与之一一对应 ✅（「每一层在前后向各广播一次」✅）。
- 大模型墙：B26 逐字 `An Issue with Data Parallelism / Each GPU saves a replica of the entire model / Cannot train large models that exceed GPU device memory`；L152 ✅。
- 溯源 L216 的许可体积：`mlsys-webrepo-LICENSE.bin` **正好 19,342 B** ✅（`.txt` 是 19,368 B，按原始取件字节算用 `.bin` 是对的）；许可名 `Attribution-NonCommercial 4.0 International` 与「CC BY-NC 4.0」✅。
- 8 个 `[[term:…]]` 全部能在 `glossary.toml` 里找到对应条目：`data parallelism`、`gradient descent`、`throughput`、`ZeRO`、`machine learning system`、`compute`、`hardware accelerator`、`latency` ✅（无悬空术语链接）。
