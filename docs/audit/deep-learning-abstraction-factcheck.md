# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 3 讲 Intro to deep learning and programming abstraction

- 核对人：**非作者**（复用 mit-6.5840 七讲记录的核对者身份 `mit65840-reviewer`）
- 核对日期：2026-09-29
- 被核对版本：`content/03-deep-learning-abstraction/index.md`
  归一化 SHA256 前16 = **1F0BC64AAA5DE138**
  （全 64 位 `1F0BC64AAA5DE1388C7F3DDCC697C6ED477CBCC579FE94951894352D7C1BE6B8`，20947 B）
- 源材料：

| # | 文件 | 用途 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-03-deep-learning-programming-abstraction.pdf.faithful.txt`（3312 行，24945 B） | **主要依据**（`.faithful.txt`，按规则不用 `text-clean`） |
| 2 | `_sources/mlsys-15442/evidence/mlsys-site-lectures.yml` | 核「第 8 讲」这条指路（上课次序） |

> **定位方式**：按上一份记录的经验，**一律用「幻灯片标题 + 逐字原文」定位**（faithful 里有换页符，行号在不同工具下会差几行）；
> 下文行号仅作辅助。

---

## 结论

**P0（事实错误）：1 条 ｜ P1（易误解/依据不足）：0 条 ｜ P2（措辞）：2 条**

---

## P0 · 事实错误

### P0-1 课件只把**第三样**配料标注为「与建模耦合」，页面写成「第二和第三样」

- **正文 L140**：「课件列的四样配料是：模型与架构、目标函数与训练技巧、正则化与归一化以及初始化，还有足够多的数据。**其中第二和第三样被特别标注为「与建模耦合」**。」
- **源（`Deep Learning Ingredients` 页，共出现两次）**逐字：
  ```
  Model and architecture
  Objective function and training techniques
  Regularization, normalization and initialization (coupled with modeling)
  Batch norm, dropout, Xavier
  Get good amount of data
  ```
  ⇒ **那个括注 `(coupled with modeling)` 只跟在第三样（Regularization, normalization and initialization）后面；第二样（Objective function and training techniques）后面没有括注。**
- **两处都这样**：这一页在课件里出现两次（`Deep Learning Ingredients` 出现两轮），**两次的括注都在第三样后面** ⇒ 不是我抽取时的偶然错位。
- **为什么算 P0**：这是本项目点名的**第一号错误类 —— 归属/范围**：页面把「课件标注的范围」从 1 项扩大成了 2 项。
  读者会据此以为「目标函数与训练技巧」也被课件归入「与建模耦合」，而这个判断是页面加上去的。
- **修在**：把「其中**第二和第三样**被特别标注为『与建模耦合』」改成「其中**第三样**（正则化、归一化与初始化）被特别标注为『与建模耦合』」。
- **备注**：如果原文页面上另有一道**跨第二、三行的括号**（纯文本抽取看不到），那么作者的读法可能来自那道括号 ——
  但**文字层的证据是「括注紧跟在第三样之后」**，且**出现两次都是如此**。⇒ 请拿原页确认一次：**若只有第三样，按上面那句改。**

---

## P2 · 措辞

### P2-1 L202 的「几千到几万量级」没有出处

正文 L202：「换成一个真实的网络，节点数是**几千到几万量级**。」
- **检索**：本讲 faithful 全文，词 `thousand|million|nodes in` ⇒ **0 命中**（课件的两问是 `What are the benefits of computational graph…`，没有给节点数量级）。
- ⇒ 这是一个**量级断言**、不是课件原话。建议标注「这是我们的估计」或删掉数量级。

### P2-2 若干机制级解释未进溯源清单（溯源已有一句一般条款，故只记 P2）

页面 L235 的溯源已经声明：「课件未展开的推论属于 CourseLingo 的讲解」并**点了 5 类**（循环网络把长度换成延迟、混合专家的便宜从别处换来、
卷积省参数的原因、注意力代价转移到显存、各家族与后续讲次的对应关系）。下面这几处同属一类但没进清单：
L52（「所有层一起学」的代价与可导链条的工程量）、L122（图数据不规整对硬件调度的挑战）、
L142（batch norm / dropout / Xavier 三者的系统含义）、L146（框架能力反过来限制模型形态）、L188（先建后跑的两个后果：图可复用、错误推迟暴露）。
⇒ **建议**：把「机制解释」也并进溯源那一句（一句话的成本）。

---

## 已核对通过（逐条附幻灯片标题 + 逐字引用）

| 正文 | 源 | 结果 |
| --- | --- | --- |
| L22 目录两行：Overview of deep learning / Programming abstractions for deep learning | 同页：`Overview of deep learning` / `Programming abstractions for deep learning` | ✅ 逐字对应 |
| L36 三个要素：模型类（带参数的函数）、损失函数（对一组给定参数我们做得有多好）、训练方法（找一组让损失最小的参数） | `Elements of Machine Learning`：`Model(hypothesis) class / A parameterized function that describes how do we map inputs to predictions`；`How well are we doing for a given set of parameters`；`Training (optimization) method / A procedure to find a set of parameters that minimizes the loss` | ✅ 三条逐字对应 |
| L36 逻辑回归的三样：逻辑回归模型 + 正则化损失 + 随机梯度下降 | 同页：`Logistic regression model` / `Regularized loss function` / `Stochastic gradient descent` | ✅ 逐字对应 |
| L48 深度学习只加一条设定：组合式多层 + 端到端训练；其余配料不变 | `Deep Learning, Key Ideas`：`End to end training: learning parameters of all layers together` / `NOTE: the other ingredients (loss and training) remains the same as other machine [learning]` | ✅ 逐字对应 |
| L56/L60 五个家族与各自定位；每节末重放清单标出当前位置 | 清单页反复出现（`An Overview of Deep Learning Models`，三次以上），条目含 `Convolutional Neural Networks` / `Recurrent Neural Networks` / `Graph Neural Networks`（+ Transformer / MoE） | ✅ 清单与「反复出现」都对 |
| L68 卷积网络六项用途：分类、检索、检测、分割、自动驾驶、图像合成 | `CNNs are widely used in vision tasks` 页：`Classification` / `Retrieval` / `Detection` / `Segmentation` / `Self-Driving` / `Synthesis` | ✅ **六项全对** |
| L72 卷积的解释：滤波器在图上滑动，每个位置做点积；权重反复使用 | 同页：`Convolve the filter with the image: slide over the image spatially and compute dot products` | ✅ 逐字对应 |
| L76 整体结构：一叠卷积层，中间夹池化/归一化/激活；引 Zeiler & Fergus 2013 | 同页：`A sequence of convolutional layers, interspersed by pooling, normalization, and activation functions`；引用行 `Zeiler … and Fergus 2013` | ✅ 结构与年份作者都对 |
| L86 循环网络：有内部状态、同一套权重每步重复用、输入输出个数任意 | `Recurrent Neural Networks`：`Key idea: RNNs have an internal state that is updated as a sequence` / `Arbitrary number of outputs` / `Arbitrary number of inputs` | ✅ 逐字对应 |
| L86 四个例子：图像生成文字、视频帧预测动作、视频描述、机器翻译 | 同组页：`e.g., image captioning` / `e.g., action prediction` / `Video captioning: sequence of…` / `Machine translation` | ✅ **四个例子全对** |
| L88 计算图必须是有向无环图，而循环网络带环；解法是展开（给定最大深度） | `How to Represent RNNs in Computation Graphs`：`Computation graphs must be direct acyclic graphs (DAGs) but RNNs have [cycles]` / `unrolling RNNs (define maximum depth)` | ✅ 逐字对应 |
| L94 循环网络缺少可并行性：前向与反向都有 O(序列长度) 个不能并行的算子；状态必须等前面全部算完 | `Inefficiency in RNNs?`：`lack of parallelizability. Both forward and backward passes have O(sequence length) unparallelizable operators` / `A state cannot be computed before all previous states have been [computed]` | ✅ **逐字对应**（O(序列长度) 是原文写法） |
| L104 注意力：把每个位置的表示当成查询，去吸收一组 values 的信息 | `Attention: Enable Parallelism within a Sequence`：`treat each position's representation as a [query] … incorporate information from a set of [values]` | ✅ 逐字对应 |
| L106 可并行度极高：不能并行的算子数量不随序列长度增长 | 同页：`Massively parallelizable: number of unparallelizable operations does not increase [with] sequence length` | ✅ 逐字对应 |
| L112 自注意力 / 掩码注意力 / 多头注意力后面会展开；「第 8 讲」 | 同页：`We will learn attention and transformers in depth later:`；排期第 8 次课 = `Case study: Transformer, Attention, Optimizations` | ✅ 三概念与讲次都对 |
| L120 图神经网络：输入是顶点与边；先聚合邻居（求和、LSTM 等）再更新目标顶点；把图传播与神经网络算子合起来 | `GNNs: Neural Networks on Relational Data` / `Neighbor Aggregation` / `Graph Neural Network Architecture` / `neural network operations` | ✅ 逐字对应 |
| L128 混合专家：让每个专家专注预测一部分情况下的正确答案；例子是 Switch Transformer | `make each expert focus on predicting the right answer for a [given case]` / `Switch Transformers = Transformers + Mixture of Experts` | ✅ 逐字对应 |
| L136 两个跨领域类比：数据管理＝SQL/执行规划器/存储引擎；数据处理＝MapReduce/容错层/工作负载迁移 | `Application affects System Design`：`Declarative language(SQL)` / `Distributed Primitive(MapReduce)` / `Fault tolerance layer` | ✅ 对应 |
| L140 四样配料（见 P0-1 更正） | 同页四行（`Model and architecture` / `Objective function and training techniques` / `Regularization, normalization and initialization (coupled with modeling)` / `Get good amount of data`） | ⚠️ 四样对，**括注范围错** ⇒ P0-1 |
| L142 三样例子：批归一化、dropout、Xavier | 同页：`Batch norm, dropout, Xavier` | ✅ 逐字对应 |
| L154 计算图定义：节点代表计算、边代表数据依赖；例子 a 乘 b 加 3，那张图有三个节点 | `Computational Graph Abstraction`：`Nodes represents the computation (operation)` / `Edge represents the data dependency between operations`；例子图上的文字：`a` `b` `mul` `add` `const` `3` | ✅ 定义逐字对应；**三个节点**（mul / add / const）也对 |
| L160 案例用 TF1 风格 API；两条提醒（今天框架换了写法、机制相同；留意抽象与实现两层） | `Case Study of Computational…`：`using TensorFlow v1 style API.` / `Note that the most deep learning frameworks now use a different style, but share the same mechanism under the hood` | ✅ 逐字对应 |
| L164 MNIST 逻辑回归：一层线性 + softmax | `Logistic Regression in TF1` 全组页；代码 `tf.nn.softmax(tf.matmul(x, W))` | ✅ 对应 |
| L171–L181 代码（placeholder `[None, 784]`、`W = zeros([784, 10])`、交叉熵、`tf.gradients(cross_entropy, [W])[0]`、`tf.assign(W, W - 0.5 * W_grad)`、`sess.run`） | 课件代码页逐词：`tf.placeholder(tf.float32, [None, 784])`、`tf.Variable(tf.zeros([784, 10]))`、`learning_rate = 0.5`、`tf.gradients(cross_entropy, [W])[0]`、`tf.assign(W, W - learning_rate * W_grad)`、`sess.run(train_step, feed_dict={x: batch_xs, y_:batch_ys})` | ✅ **关键数字 784 / 10 / 0.5 全对**（页面把训练循环略去，已在溯源声明「按原文给出的机制缩写重排」✅） |
| L186 最后一行才是真正开始计算；课件在那一页标了 real execution happens here | 同页：`Real execution happens here!` | ✅ **逐字对应** |
| L198 反向那一段接上 log-grad、softmax-grad、除以批量大小、矩阵乘转置等节点 | `Computational Graph Construction by Step` 组页 + `Automatic Differentiation, more details in…` | ✅ 步骤与页面一致 |
| L202 课件在这一页留了两问（计算图抽象带来什么好处、这之上还能做哪些优化） | 同页：`What are the benefits of computational graph [abstraction]?` | ✅ 逐字对应（第二问见 P2-1 备注） |
| L210 两种写法的名字：`define then run` 与 `define and run` | `Imperative Computational Graph Construction`：`TF1 style API uses a [define then run]` / `First construct the whole computational graph, then run the computation` / `[PyTorch] and other frameworks uses a [define and run]` / `constructs the computational graph on the fly, along side the computations` | ✅ **两个名字都是课件原话**（注意：通用术语里 PyTorch 常被称为 define-by-run，但本页说的是「课件用的名字」，与课件一致 ✅） |
| L212 可调试性：边算边建图能立刻拿到结果；先建后跑中间态难观察 | 同页：`Define and run gives more flexibility to programmer` | ✅ 方向对应 |
| L214 全局优化：先建后跑能看到整张图做整体改写 | 同页：`See the entire computational graph to do global optimization` | ✅ 逐字对应 |
| L216 仍是活跃方向，混合方案如即时编译 | 同页：`Active topic of research, hybrid approaches such as JIT compilation` | ✅ 逐字对应 |

**配图**：15 张图做了**定向检索**（关键词 `耦合`、`784`、`0.5`、`三个节点`、`几千`、`2013`、`六项`、`自注意`、`多专家`、`Switch`、`Xavier`、`LSTM`），未发现与正文冲突；
其中**「耦合」在 15 张图里 0 命中** ⇒ 图里**没有**复述 P0-1 那条被扩大的注解（所以那一处的修法只需改正文）。
**说明**：这是**定向**检索，不是逐张通读 ⇒ 见「我核不到的」。

---

## 我核不到的（诚实记录）

1. **P0-1 的最后一步**：文本层能证明「括注紧跟在第三样之后、出现两次都如此」，但**文本层看不到版面上有没有一道跨行的括号**。
   ⇒ **结论的性质**：我能确定「**文字层面只标注了第三样**」；我不能排除「版面上另有一道覆盖第二、三样的视觉标注」。**这一处请拿原页图定案。**
2. **配图**：只做了上面那组关键词的**定向检索**，**没有**逐张通读 15 张图的全部可见文字与 `desc` ⇒ 图与正文之间可能仍有我这次没检索到的口径差异（第 2 讲那条 `desc` 用词错误就是这样被发现的）。
3. **机检指标**（`audit_content.py` 等）与配图几何：不在本次范围。

---

## 覆盖面（附录十二）

- **已验**：目录两行；三个要素与其逻辑回归例子；深度学习的两条关键想法与那句 NOTE；五个家族；卷积六项用途 + 卷积定义 + 整体结构 + Zeiler & Fergus 2013；
  循环网络（内部状态、任意输入输出、四个例子、DAG 与展开、O(序列长度) 不可并行算子）；注意力（查询/values、massively parallelizable、三概念与讲次）；
  图神经网络（关系数据、邻居聚合、LSTM）；混合专家（Switch Transformer）；两个跨领域类比；四样配料与括注（⇒ P0-1）；三样例子；
  计算图定义与 a*b+3 三节点；TF1 案例（784 / 10 / 0.5 / real execution here）；四步建图；两种构造方式与各自代价 + JIT 走向。
- **未验**：上面「我核不到的」3 条。

---

**核对人声明**：本记录只覆盖开头那个哈希的版本（`1F0BC64AAA5DE138`）。按附录五，对其它版本的结论不成立。
本记录只读正文、不修改任何 `content/` 文件；`status` 由 Lead 处理。
