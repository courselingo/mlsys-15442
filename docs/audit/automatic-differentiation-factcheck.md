# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 4 讲 Week 3: Automatic Differentiation

- 核对人：**非作者**（`fig-pruner`。**没有**参与本讲任何一轮写作，也没有与作者讨论过本讲内容）
- 核对日期：2026-09-29
- 被核对版本：`content/04-automatic-differentiation/index.md`
  归一化 SHA256 前16 = **9168F8474E06C53A**
  （全 64 位 `9168F8474E06C53A7D433D29132417B648324AAE57AC5FEDFE8B4BDDC778DA59`，19213 B；与 Lead 派单哈希一致 ✅）
  - 14 张配图（前 16 位）：`-1 78D05FC931FF9AEE` · `-2 0EA5229DEAA2A3DD` · `-3 65EDAE52DBCA85F8` · `-4 1DE1A69C95F0273F` ·
    `-5 62E98CF0AA78D788` · `-6 E1E5F9C344ECD4EF` · `-7 5234FA5D58288FE6` · `-8 24FC201836189624` · `-9 619A8FB3ECD27A6B` ·
    `-10 73D49DD29F965F56` · `-11 0A16DE4996D72FFD` · `-12 2D59A2FDB2E3DF14` · `-13 5A22D0CA941C9457` · `-14 D072BBDE4D23383D`
- 源材料（本次实际依据的，逐个列出）：

| # | 文件 | 用途 / 说明 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-04-automatic-differentiation.pdf`（488,380 B，**26 页**） | 权威源；页脚编号与 PDF 页码 1:1（已抽查 p4／p14／p21／p22 的页脚 = 4／14／21／22）⇒ 下文一律用「pN」定位 |
| 2 | 同目录 `.faithful.txt`（23,160 B，SHA256 前16 `E08ECAEF6703C0ED`） | **主要依据**（按项目约定用 faithful，按「幻灯片标题 + 逐字原文 + 页码」定位，行号不作坐标） |
| 3 | 同一 PDF 的 **pypdf 文本层** | **补充手段，只用于 faithful 里字形乱码的公式页**（p5/p6/p7/p9/p10/p13/p14/p21/p22/p26）；见「我核不到的」第 1 条 |
| 4 | 同目录 `.embedded.txt`（20,345 B） | **实测是字体二进制**：`OS/2`/`cmap`/`glyf` 各 4 命中，课程文字 0 命中 ⇒ **未用于任何结论** |
| 5 | `content/03-deep-learning-abstraction/index.md`、`content/02-introduction-to-mlsys/index.md` | 核本页的三处跨页指路（L20／L124／L159） |

---

## 结论

**P0（事实错误）：0 条 ｜ P1（易误解/依据不足）：2 条 ｜ P2（措辞）：6 条**

---

## P0 · 事实错误

**0 条。**

（逐条回源范围内，没有找到与课件相冲突的断言。源里可核的定义、公式、框架名、页脚编号都对得上，见最后一节抽样清单。）

---

## P1 · 易误解或依据不足

### P1-1 L179 的「那个年代的模型主要是 CNN，网络是手写的一长串层，反向硬编码」在课件里没有依据

- **正文 L179**：「第一种叫反向传播：直接在正向那张图上倒着跑，不新建节点。**课件注明**它是第一代深度学习框架的做法，例子是 caffe 与 cuda-convnet。**那个年代的模型主要是 CNN，网络是手写的一长串层，反向也就跟着硬编码进去。**」
- **源（p21，标题 `Reverse Mode AD vs Backprop`）**该页正文**只有四条 bullet**（pypdf 与 faithful 一致）：
  ```
  • Run backward operations the same forward graph
  • Used in first generation deep learning frameworks (caffe, cuda-convnet)
  • Construct separate graph nodes for adjoints
  • Used by modern deep learning frameworks
  ```
- **全篇检索（faithful 与 pypdf 两个抽取器都查）**：`CNN` **0**、`convolutional` **0**、`hardcod` **0**、`handwritten` **0**；`caffe` 1、`convnet` 1（就是上面那两条 bullet）。
- ⇒ 加粗那句是**我们没有标出处的补充**，而它紧跟在「课件注明…」之后，读者会当成课件的话。**建议**：把它明确标成我们的背景补充（或删）。
- **降级说明**：本页溯源那句「这类推论**包括**：…」是非穷尽条款，若按此口径，本条可降为 P2。我按正文的就近读法先记 P1，**请 Lead 裁决**。

### P1-2 L68 的「两个输入」例子站不住，且与课件的例子不同

- **正文 L68**：「用一个小例子就能看清：**两个输入的函数，求两个偏导时同一个乘积项会出现两次**；输入变成三个、四个，重复的次数继续涨。」
- **源（p7，标题 `Symbolic Differentiation`）**给的例子是 **n 个输入的连乘**（pypdf 逐字）：
  ```
  𝑓 𝜃 = ∏(i=1..n) 𝜃𝑖        𝜕𝑓(𝜃)/𝜕𝜃𝑘 = ∏(j≠k) 𝜃𝑗
  Cost 𝑛(𝑛 − 2) multiplies to compute all partial gradients
  ```
- n=2 时两个偏导分别是 θ₂ 与 θ₁，**没有乘积项，更没有「同一个乘积项出现两次」**；重复计算的现象要到 n≥3 才出现。
- ⇒ 这条不是归属问题，是**例子本身站不住**：建议直接改用课件那个 n 输入连乘的例子（顺带把 P2-1 的原式一起写上）。

---

## P2 · 措辞

1. **L66「课件给的量级是 O(n²) 次乘法」**：课件逐字是 `Cost 𝑛(𝑛 − 2) multiplies to compute all partial gradients`。「n(n−2) 的量级是 n²」这句本身没错，但既然写「课件给的」，把原式 `n(n−2)` 写出来更准、也和 L68 的例子里外一致。
2. **L70「一个真实模型的参数有几百万到几千亿个」与 L108「输入有几百万个（模型参数）」**：全篇 `million`／`billion`／`trillion` **各 0 命中**（课件只说 `large 𝑛`）。这是我们的现实参照，建议标成我们的补充或给出来源。
3. **记号改写未注明**：L193「前向写成 **Y** = XW」，课件逐字是 `Forward matrix form: 𝑍 = 𝑋𝑊`（标量输出才是 `v = f(Z)`）。改用 Y 可以，但建议在溯源里记一句「矩阵乘结果的记号由课件的 Z 改写为 Y」。
4. **L193「再与 X 的转置相乘，得到 W 的伴随」**：课件的 `Reverse matrix form` **只有 X̄ = Z̄Wᵀ 一条**（pypdf 逐字 `ത𝑋 = ҧ𝑍𝑊𝑇`）。页面给的 `W̄ = XᵀZ̄` 数学上对（也是训练真正要的那一项），但**该页未见 W̄ 的式子**；建议标成我们的补充，或写成「（W 的伴随同理）」。
5. **L34「课件把可选的路线摆成三条」与 L42 的三句定位**：课件在引言里分别讲了数值微分（p5–p6）与符号微分（p7），**没有一页把三条路线并列**——`Outline`（p2／p3）只有两条：`General introduction to different differentiation methods` 与 `Reverse mode automatic differentiation`，全篇 `three` **0 命中**。而 L42 的「数值微分不需要任何数学知识」「自动微分两边都要」在课件里也没有对应文字（`math knowledge` 0 命中；课件对数值微分的三条是 `Directly compute…／A more numerically accurate way…／Suffer from numerical error, less efficient to compute`）。这三句属本页的概括（溯源那句「包括」覆盖得住），但「课件把…摆成三条」建议改成「本讲把三条路线摆在一起看」。
6. **L58「取一个方向向量」**：课件逐字 `Pick 𝛿 from unit ball, check the above invariance`——**「从单位球里取」这个限定被略去**（不影响做法，补上更贴合原文）。

---

## 已逐条回源、未发现问题的（抽样清单）

**关键句逐字对得上**（页码后为逐字原文）：

- p4：`Computing the loss function gradient with respect to hypothesis class parameters is the most common operation in machine learning` ✅（L22）
- p5：`Directly compute the partial gradient by definition` / `A more numerically accurate way to approximate the gradient` / `Suffer from numerical error, less efficient to compute` ✅（L48）
- p6：`However, numerical differentiation is a powerful tool to check an implement of an automatic differentiation algorithm in unit test cases` ✅（L58）
- p7：`Write down the formulas, derive the gradient by sum, product and chain rules` / `Naively do so can result in wasted computations` ✅（L62）
- p8：`Each node represent an (intermediate) value in the computation. Edges present input output relations.` ✅（L80）
- p9：`Define ṿ𝑖 = 𝜕𝑣𝑖/𝜕𝑥1` / `We can then compute the ṿ𝑖 iteratively in the forward topological order of the computational graph` ✅（L92／L98）；**乘法那一行的例子**逐字 `ṿ4 = ṿ1𝑣2 + ṿ2𝑣1 = 1 × 5 + 0 × 2 = 5`（即 L94「乘法那一行，导数按乘积法则展开成两项」）✅；加法行 `ṿ6 = ṿ3 + ṿ4` ✅
- p10：`For 𝑓: ℝ^𝑛 → ℝ^𝑘, we need 𝑛 forward AD passes to get the gradient with respect to each input` / `We mostly care about the cases where 𝑘 = 1 and large 𝑛` ✅（L108）
- p12：`Define adjoint ̄𝑣𝑖 = 𝜕𝑦/𝜕𝑣𝑖` / `compute the ̄𝑣𝑖 iteratively in the reverse topological order` ✅（L120／L122）
- p13：`Define partial adjoint 𝑣𝑖→𝑗 = ̄𝑣𝑗 𝜕𝑣𝑗/𝜕𝑣𝑖 for each input output node pair 𝑖 and 𝑗` / `We can compute partial adjoints separately then sum them together` ✅（L132）
- p14：**伪代码逐行结构一致**——`def gradient(out):` / `node_to_grad = {out: [1]}` / `for 𝑖 in reverse_topo_order(out):` / `𝑣̄𝑖 = σ𝑗 𝑣𝑖→𝑗 = sum(node_to_grad[𝑖])` / `for 𝑘 ∈ 𝑖𝑛𝑝𝑢𝑡𝑠(𝑖):` / `compute 𝑣𝑘→𝑖 = ̄𝑣𝑖 𝜕𝑣𝑖/𝜕𝑣𝑘` / `append 𝑣𝑘→𝑖 to node_to_grad[𝑘]` / `return adjoint of input 𝑣𝑖𝑛𝑝𝑢𝑡`，三条旁注 `Dictionary that records a list of partial adjoints of each node` / `“Propagates” partial adjoint to its input` / `Sum up partial adjoints` ✅（L144–L157；L157 第 1、2 个细节与旁注一一对应）
- p16：`NOTE: ̄𝑣4 is identity function f(x)=x` ✅（L169）
- p21：`Used in first generation deep learning frameworks (caffe, cuda-convnet)` / `Used by modern deep learning frameworks` ✅（L179／L181）
- p22：`Forward matrix form: 𝑍 = 𝑋𝑊` / `Reverse matrix form: ത𝑋 = ҧ𝑍𝑊𝑇` ✅（L193，记号的差异见 P2-3／P2-4）
- p24：`Discussions` / `What are the pros/cons of backprop and reverse mode AD` ✅（L185「课件在这一页没有下结论，只留了一个讨论题」）
- p25：`The result of reverse mode AD is still a computational graph` / `We can extend that graph further by composing more operations and run reverse mode AD again on the gradient` / `Part of homework 1` ✅（L207）
- p26：`Key take away: Define “adjoint value” usually in the same data type as the forward value and adjoint propagation rule. Then the sample algorithm works.` / `Do not need to support the general form in our framework, but we may support “tuple values”` ✅（L205）

**跨页指路三处都对**：

- L20「第 2 讲把 machine learning systems 拆成**七层**，其中**第一层**就是自动微分」✅（L2 页 L22「拆成七层并排在一个栈里」、L46「栈的第一层是 automatic-differentiation」）
- L124「第 2 讲说过**显存是训练的天花板**」✅（L2 页 L168 小节标题「第 4、5 层：内核从哪来，显存为什么是天花板」）
- L159「图里不能有环，这一点在第 3 讲讲**循环网络**时出现过，那里是靠**展开**消掉自环的」✅（L3 页 L88「computational-graph 必须是有向无环图，而循环网络带自环。它的解法是把循环展开」）

**14 张配图的 `alt` 与对应幻灯片一致**（逐张比对：p4 三要素／p5–p6 数值微分两条＋梯度检查／p7 符号微分／p8 计算图／p9 前向两列／p10 前向限制／p12 伴随量两排／p13 多路径／p14 算法三步／p15–p20 反向建图／p21 两种实现／p22 张量／p25–p26 两个延伸）。

---

## 我核不到的（诚实记录）

1. **faithful 里的字形乱码，以及我用的补充手段**
   `.faithful.txt` 有不少 run 是「整段位移」的字形码。例：p4 的 `+RZ³ZHOO´DUHZHGRLQJIRUDJLYHQ` 解出来是 `How well we are doing for a given`（位移 +0x1D）；另一些 run 用别的字体表（p7 的 `Cost J : J F t ; multiplies…` 就是这种）。
   ⇒ **对这些页我另用同一 PDF 的 pypdf 文本层取证**（p5／p6／p7／p9／p10／p13／p14／p21／p22／p26），得到可读公式；`n(n−2)`、`ṿ4 = ṿ1𝑣2 + ṿ2𝑣1`、伪代码、`𝑍 = 𝑋𝑊`／`ത𝑋 = ҧ𝑍𝑊𝑇` 都是这样核到的。
   ⇒ **声明**：本记录**没有**在 faithful 的乱码 run 上下任何结论；pypdf 输出与 faithful 是**同一个 PDF 的两个抽取器**，不是第二个来源。p7 那个乱码 run 我**没有**逐字解码成功（只解出 `Cost … multiplies to compute all partial gradients` 的骨架），`n(n−2)` 是从 pypdf 拿到的。
2. **p22 图形内部（非文本对象）**：我只核到该页的**文本对象**。若 `W̄` 画在图形里而不在文本框中，我读不到（P2-4 的结论以此为前提）。
3. **`desc` 与图内几何**：本次只核正文与 14 张图的 `alt`，**没有**逐张读 SVG 的 `desc`／几何／墨迹（L2 出过 `desc` 把「原图」写成「原因」而机检抓不到的先例，建议单独过一遍）。
4. **课件之后的内容**：L171「后面讲 kernel 生成与图级优化时，动的正是这两张图」、L124「后面讲内存优化的那一讲」——只核到讲次清单里存在对应讲次（`ml-compiler-gemm`／`ml-compiler-data-layout`／`memory-optimization`），未读那些讲次的课件。
5. **课件之外的通用事实**（CNN 时代的框架形态、模型参数规模量级）：我按「课件没说」记录，**没有**去核外部文献 ⇒ 不判对错，只判「不当成课件的话」。
6. **检索范围与词**（否定性结论一律附范围）：
   - 全文：`faithful` 的 **26 段逐段读完**（p001–p026）；pypdf 文本层覆盖 p5／p6／p7／p9／p10／p13／p14／p21／p22／p26（其余页 faithful 可读，未再交叉）。
   - P1-1：`caffe` `cuda-convnet` `convnet` `CNN` `convolutional` `hardcod` `handwritten`（faithful 与 pypdf 两个抽取器都查，命中数见 P1-1）。
   - P2-2：`million` `billion` `trillion` `parameters`。
   - P2-5：`three`、`math knowledge`、`unit ball`。
   - 跨页：L2／L3 页面的 `七层`／`第一层`／`天花板`／`循环`／`展开`／`自环`。

---

**核对人声明**：本记录只覆盖基线前16 `9168F8474E06C53A`（作者交付 `6cbe8c4`；14 张配图哈希已一并钉住）。页面或配图再改动，结论不自动成立（`附录五`）。本记录**不修改**任何正文、配图或 `status`。
