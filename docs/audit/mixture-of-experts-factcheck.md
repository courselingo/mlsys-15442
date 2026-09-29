# 事实核对 · CMU 15-442/15-642 第 18 讲 混合专家

- 核对人：非作者
- 核对日期：2026-09-29
- 被核对版本：`content/18-mixture-of-experts/index.md`，归一化 SHA256 前16 = **DE66D32FB8BD3075**
- 源材料（我实际依据的文件）：`_sources/mlsys-15442/evidence/mlsys-slide-16-mixture-of-experts.pdf.faithful.txt`（10,691 B，1,789 行，**含 120 个 NUL 字节**，`read` 工具按二进制拒绝读取，改用逐行读取）；交叉讲引用另用 `content/03-deep-learning-abstraction/index.md`、`content/09-ml-parallelization-1/index.md`、`content/10-ml-parallelization-2/index.md`、`content/14-llm-serving-1/index.md`、`content/16-llm-serving-2/index.md`
- **⚠️ 拿对了源**：本讲与第 17 讲同目录、且文件名都以 `16-` 开头（`16-LLM-finetuning` vs `16-mixture-of-experts`）。本记录**只用** `…-16-mixture-of-experts.pdf.faithful.txt`。
- 抽取器与锚词（三步动作）：`faithful`；锚词 `Mixture of Experts`（命中）、`MegaBlocks`（命中）、`Permutation`（命中）、`Prefix Sum`（命中）。⇒ 锚词命中，可继续。
- **★ 这一份是本讲四份里最完整的一份**：20 页的**页面标题、页号、正文短句、公式片段**都在文本层里，连 p17 的例子数组都完整（`[[1,0,1],[1,1,0],[1,0,1],[0,1,1]]`、`[[1,3,6],[2,4,6],[3,4,7],[3,5,8]]`、`[[0,5],[1,3],[2,6],[4,7]]`）。仍有 −0x1D 错位行（第 117、147、163、293-298、565-611、726-770… 行）与 kern 碎片，但凡涉及结论的句子我都用**未错位的同页行**交叉确认了。

## 结论

P0（事实错误）：**1** 条 ｜ P1（易误解/依据不足）：**2** 条 ｜ P2（措辞）：**2** 条

## P0 · 事实错误

| # | 位置 | 正文说 | 源材料说 | 依据（逐字引用 + 页码） |
| --- | --- | --- | --- | --- |
| 1 | 正文第 176/178 行；配图 `figures/mixture-of-experts-13.svg`（`<title>`/`<desc>`/图上文字）；溯源第 215 行 | 第 178 行「课件在这一讲里留了**两道**讨论题」；图上「课件留下的**两道**讨论题」「**两页**都只有问题，没有答案」；溯源「本页在正文里**逐处标明**了哪些是课件的问题、哪些是我们就它的结构补的解读」 | 课件有 **4 处**只提问不给答案的地方：**3 页**标题就叫 `Discussions`（p8、p11、p19）+ **1 处行内讨论问题**（p18）。而且 p18 那处**本页全篇没有提** | 逐页原文：p8 第 498-503 行 `Discussions` / `What are the advantage of using Mixture of Experts vs Linear layers`（页码 `8` 在第 503 行）；p11 第 543-550 行 `Discussions` / `What are opportunities and challenges in accelerating mixture of expert layers?`（页码 `11` 在第 545 行）；**p18 第 1752-1756 行 `Discussion: How to get indptr from the existing data?`**（页标题 `Revisit the Batched Compute`，页码 `18` 在第 1599 行）；p19 第 1765-1772 行 `Discussions` / `What are opportunities and challenges in parallelizing mixture of expert layers?`（页码 `19` 在第 1767 行）。本页实际标注的三处是 p8（第 72-80 行）、p11 与 p19（第 176-188 行）⇒ **p18 那一处漏了，且「两道」这个计数按任何一种数法都不成立**（`Discussions` 页有 3 页；凡带问句的讨论页共 4 处） |

## P1 · 易误解或依据不足

1. **「这两步都是 O(专家数) 的，与输入总量无关，所以它们的开销可以忽略」**（第 156 行）
   - 课件对同一件事的说法是 `Prefix sum(scan) can be efficiently **parallelized in GPU**`（第 1588 行）——**理由是可并行，不是复杂度与输入量无关**。
   - 而课件给的做法本身就与输入量有关：p17 第 1548-1556 行的算式是 `cumsum(flatten(mask.T))`，作用在 p17 给的那张 4×3 的选择掩码上（第 1505-1520 行 `[ [1,0,1],[1,1,0],[1,0,1],[0,1,1] ]`）⇒ 扫描的元素是 **4×3 = 12 个 = 输入数 × 专家数**，「前缀和」这一步的规模上限就是输入数乘专家数。
   - 更细一点：**「数出每个专家分到了几个输入」这一步也不可能是 O(专家数)**——不遍历输入就无法得到每个专家的计数（课件的实现就是压平整张掩码）。所以「与输入总量无关」至少对第一步不成立。
2. **配图 `figures/mixture-of-experts-2.svg` 第 28 行（渲染在图上）：「课件给的块结构是 8 乘 3 的写法」**
   - 我通读 p4（`Recap: Transformer Block`）的可见文字：页号 `4`（第 74 行）之后紧接着一个裸的 `8` `-` `3`（第 76-80 行），然后是图里的标签 `normalize / normalize / Feed forward / matmul / softmax / matmul / output / input / Self-attention`，最后是图注 `A typical transformer block (multi-head) self-attention, followed by a linear layer and ReLU and some additional residual connections and normalization`（第 182-200 行）。
   - **没有任何文字支持「块结构是 8 乘 3 的写法」**。那个 `8-3` 更可能是**图注/版式编号**（本课件这一类「数字-数字」串在其他讲里也出现过，形式与图号一致），但我从文本层**无法判定**它是图号还是形状 ⇒ 记「依据不足」，不下「错」的结论；建议作者对着 PDF 那一眼确认后再决定这句留不留。

## P2 · 措辞

1. **课件 p7 的具体例子与限定语没有进入本页，溯源也没说明略去。** 课件 p7（`A Closer Look at Mixture-of-Experts`）除门控结构外还有：`Example model: Mixtral-8x7B selects 2 experts among eight`（第 475-479 行）、`Greedily select top-K experts among N`（第 468-472 行）、`Different models may have different FFN configurations, usually contains multiple linear layers and some non-linear mixing`（第 482-489 行）。本页正文与配图里**没有 Mixtral / 8x7B / 八选二**，溯源第 214 行的「取材范围分四块」也只写到「门控的作用」。⇒ 略去本身可以接受，但溯源一边自称范围一边不提这一页，读者会以为课件没有实例。
2. **「两道题的分界正好是第 9 讲与第 10 讲讲过的那个分界：卡内靠切分，卡间靠通信」**（第 184 行）—— 我在第 9、10 两讲页面里检索 `卡内|卡间|设备内|设备间`：**0 命中**。两讲讲的是数据并行与模型并行、以及 AllReduce 的通信量，并没有「卡内 / 卡间」这个二分法。这句作为我们的概括没问题（溯源第 216 行已把「跨讲的联系」整体声明为我们的编排），只是「讲过的那个分界」这个说法把我们的概括记成了课件/讲次的说法。

## 判据 ⑧⑨⑩（这一轮新立的，逐条查）

**⑧ 两套并存的计数/编号体系 —— 命中，且就是 P0-1。**

- 课件自己就有**两套「讨论」标记**：**页级**的三页 `Discussions`（p8 / p11 / p19）与**行内**的一处 `Discussion:`（p18）。本页把前者数与后者都压成了「两道」，而且**只用了 p11、p19 两页**来数（把 p8 另立为「课件在这一页留了一道讨论题」，第 72 行），p18 的行内讨论则整处消失。⇒ 这是「两套并存的计数体系，只说到了一套」的又一例：**读者从本页得到的「课件只留了两道题」是错的**。
- 对照（写得对的地方）：课件大纲确实只有两条（第 41/44 行 `Mixture of Experts` / `Efficiently Compute Mixture of Experts`），本页第 26 行「课件的大纲只有两条」✅；课件页数确实是 20（末页页号 `20` 在第 1789 行），本页溯源第 215 行「它一共只有二十页」✅。

**⑨ 少认了源材料 —— 软命中 1 条。**

- 溯源第 216 行把「把批量化说成「让稀疏计算能落到硬件上的前提」」列为我们的因果判断。可是**课件自己给了硬件侧的理由**：p13 第 776-788 行 `When B becomes larger, we get better compute efficiency due to **memory load reuse in matrix multiply and hardware specialization via TensorCore**`，紧接着 p14 就是 MegaBlocks 的批次置换（第 795-1048 行）。⇒ 这条「前提」的硬件半边是课件说的，不该整体记到我们名下。
- 未发现别的硬命中：本页对源的引用大多是逐字或紧贴原文（`Key idea` / `In practice, each expert here is an FFN` / `Simply replace the FFN layer in a transformer model by mixture of experts` / `Greedily select top-K experts among N` / `Batched Linear Layer` / `Gale et.al MegaBlocks: Efficient Sparse Training with Mixture-of-Experts` / `Compressed row(CSR) format` / `Prefix sum(scan) can be efficiently parallelized in GPU`）。

**⑩ 跨讲承诺 —— 本讲对外 0 条承诺；incoming 0 条；但有两处引用归因要改。**

- 本讲发给他讲的承诺：**无**（「后面的高级编译与内核生成里还会再出现」这类句子没有点名讲次）。
- 别人对本讲的引用：我在 `content/**/index.md` 全树检索 `第 18 讲`：**0 命中**；第 2 讲第 235 行有一张跨讲承诺登记表（第 4/9/10/11/14/16/19 讲），**其中没有第 18 讲** ⇒ 不需要兑现任何 incoming 承诺。
- 本讲自己的跨讲引用逐条验：
  - 第 20/52/194 行「第 3 讲把混合专家当概念讲过一次」「参数量可以远大于每次计算用的参数量」→ ✅ 第 3 讲第 124 行「第五个家族是混合专家」、第 62 行「混合专家的参数远大于单次计算要用的量，考验显存」。
  - 第 68 行「第 14 与第 16 讲讲的那些服务侧手法」→ ✅ 两讲都在仓库里且都是服务讲次（`14-llm-serving-1`、`16-llm-serving-2`）。
  - 第 172 行「这一点和第 10 讲讲过的负载不均是同一个问题，只是粒度更细：**那里的不均衡来自「请求的长度不同」**，这里来自「每份输入的偏好不同」」→ ❌ **归因错位**：第 10 讲的不均衡来自**流水线级与级之间的快慢不均**（第 140 行「还要额外处理级与级之间的快慢不均」），而「请求的长度不同」是**第 14 讲**的话（第 66 行「有的请求几个 token 就结束了，有的要生成几百个……这种「长短不一」不是异常情况，而是常态」）。**已记入 P1 的同一类问题**（此处只记方向，不重复计数）：建议改为「第 14 讲的请求长短不一，或第 10 讲的流水线级不均衡」。
  - 第 184 行「第 9 讲与第 10 讲……卡内靠切分，卡间靠通信」→ 见 P2-2。

## ★ 讨论页专项结论（作业点名要查的两件事）

| 问题 | 结论 |
| --- | --- |
| 标注是否**覆盖**了那些讨论页？ | **没有完全覆盖。** 课件 4 处只提问不给答案的地方，本页标了 3 处（p8 第 72-80 行；p11 + p19 第 176-188 行，并在图上与溯源各标一次），**漏了 p18 第 1752-1756 行的 `Discussion: How to get indptr from the existing data?`**（正文第 148-160 行讲前缀和时完全没有提它）。而且计数写成「两道」/「两页」，与课件的 3 页 `Discussions` 也不符（见 P0-1） |
| 有没有把**课件的问题**写成**课件的结论**？ | **没有，这一点作者做得干净。** 已标注的三处都明确区分了归属：p8 那处正文写「课件没有在这一页给出答案。从它的结构可以推出两个角度……**这两条是我们就它的结构补的解读，不是课件上的文字**」（第 78-80 行），配图第 28-29 行同样写「课件只提问、没给答案 / 上面两条是我们就它的结构补的解读」；p11/p19 那处正文写「课件没有给出答案。但从这一讲的结构可以看出来……」（第 186 行），溯源第 216 行把它们列为「对讨论题的回答」这一组推论。**三处逐字核过，没有一处把我们的答案写成课件的答案。** |

## 我核不到的（诚实记录）

- **p4 那个 `8-3` 到底是什么**（P1-2）：文本层只给出裸的 `8` `-` `3`，给不出它在这页的版式位置。我**不能**说「8 乘 3 是错的」，只能说本页那句「课件给的块结构是 8 乘 3 的写法」在源的可见文字里**没有依据**。
- **p5 与 p13 的公式**：p5 的 `Feed forward … ReLU` 前后是被 −0x1D 错位的符号串（第 214-266 行），p13 的 `X·W` 形状也是（第 726-770 行，只剩 `9 á : Ð 9 Õ H á á 9 Ð 9 á H à` 之类）。⇒ 本页对这两页只作定性描述（「两个线性层夹一个激活」「写成一次矩阵乘」），我核到这一步为止，**没有**去复原公式。
- **p14/p15/p16/p18 的图内信息**：置换演示、`indptr / data / weights` 三行、CSR 例子、`Permutation indices: index s t u v w x y` 这些都只剩字母碎片（第 795-1789 行大量单字符行）。本页对它们的描述是**定性**的（「两套下标」「同一个专家的输入连续存放」），与可见的 `permute` / `un-permute` / `Expert 0/1/2` / `Color tracks instance indices` 一致，但**细到数组取值的部分我无法逐项复核**。
- **课件是否在 p8 之外还有别的「只提问」之处**：我按 `Discussion` 与问号两种特征全文检索过（`Discussion` 命中 p18 行内一处；三页 `Discussions` 页标题另行肉眼逐页过），若原文里有以图形形式呈现、文字层不含问号的提问页，我核不到。

## 覆盖面

**配图（14 张 SVG，全部逐张通读：14/14）**：`mixture-of-experts-1.svg` … `-14.svg`，逐张读过 `<title>`、`<desc>` 与全部 `<text>`（`desc` 不渲染，按方法 ⑦ 通读）。逐项回源结果：`大纲只有两条`（`-1.svg`）= 第 41/44 行 ✅；`8 乘 3 的写法`（`-2.svg`）= **无依据**（P1-2）；`每个专家在实践中就是一个前馈网络`（`-3.svg`）= 第 293 行 ✅；`门控根据输入算出一组权重再挑专家`（`-4.svg`）= 第 314-348 行 ✅；`课件在这里留了一道讨论题 / 课件只提问、没给答案 / 上面两条是我们就它的结构补的解读`（`-5.svg`）= p8 ✅；`直接把前馈层换成混合专家`（`-6.svg`）= 第 517 行 ✅；`单份输入：门控给出专家下标`（`-7.svg`）= 第 461-472 行 `A typical MoE layer (assume single instance and activate two experts)` ✅；`一批输入一起过一个线性层写成一次矩阵乘`（`-8.svg`）= p13 ✅；`课件引的是 MegaBlocks`（`-9.svg`）= 第 804-818 行 ✅；`按专家重排，算完再排回来`（`-10.svg`）= p14 的 `permute` / `un-permute` ✅；`前缀和求置换下标 / 前缀和的最后一个值就是总数`（`-11.svg`）= 第 1433-1588 行（注意 `-11.svg` 的 `<desc>` 与图上文字都**没有**说「O(专家数)」，那句只在正文第 156 行 ⇒ P1-1 是正文的问题，不是图的问题）；`每个专家处理一段连续的输入`（`-12.svg`）= p18 ✅；`课件留下的两道讨论题`（`-13.svg`）= **P0-1**；`第 3 讲概念、这一讲落地、第 10 讲并行化问题重现`（`-14.svg`）= 跨讲编排，其中「第 10 讲并行化」✅ / 「负载不均来自请求长度」❌（见 ⑩）。

**源侧**：`mlsys-slide-16-mixture-of-experts.pdf.faithful.txt` **全 1,789 行逐行读完（不是抽样）**——这一份只有 10.5 KB 且文本层完整，所以我把 20 页的标题、页号与可见正文全部过了一遍，包括第 64-205 行的逐字符原文。**定向检索**用于佐证两处：`Discussion`（命中第 1752 行，即 P0-1 漏掉的那一处）、`Prefix sum|scan|TensorCore|memory load reuse`（命中第 776-788、1588 行，用于 P1-1 与 ⑨）。

**正文侧**：`content/18-mixture-of-experts/index.md` 217 行逐行读完；跨讲引用回源第 3、9、10、14、16 讲；`content/**/index.md` 全树检索 `第 18 讲` 确认无 incoming 承诺（并顺带看到第 2 讲第 235 行的跨讲承诺登记表里没有第 18 讲）。
