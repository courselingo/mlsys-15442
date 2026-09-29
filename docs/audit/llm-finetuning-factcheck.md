# 事实核对 · CMU 15-442/15-642 第 17 讲 LLM 微调技术

- 核对人：非作者
- 核对日期：2026-09-29
- 被核对版本：`content/17-llm-finetuning/index.md`，归一化 SHA256 前16 = **293EB5B01D9C3A2B**
- 源材料（我实际依据的文件）：`_sources/mlsys-15442/evidence/mlsys-slide-16-LLM-finetuning.pdf.faithful.txt`（22,164 B，4,176 行，**含 263 个 NUL 字节**，`read` 工具按二进制拒绝读取，改用逐行读取）；交叉讲引用另用 `content/11-memory-optimization/index.md`、`content/05-optimizing-linear-algebra/index.md`、`content/16-llm-serving-2/index.md`
- **⚠️ 拿对了源**：本讲的源是 `…-16-LLM-finetuning.pdf.faithful.txt`（仓库讲次 17 = 课件号 16）。同一目录下还有 `…-16-mixture-of-experts.pdf.faithful.txt`，**那是第 18 讲的源**，本记录一字未用。
- 抽取器与锚词（三步动作）：`faithful`；锚词 `LoRA`（命中，含 `LORA: Low-Rank Adaption of Large Language Models. Hu et al. 2021`）、`QLORA`（命中 `QLORA: Efficient Finetuning of Quantized LLMs`）、`Side Tuning`（命中 `Quantized Side Tuning`）、`Cobus Greyling`（命中，第 378 行 `Figure credits: Cobus Greyling`）。⇒ 锚词命中，可继续。
- **★ 这份 faithful 的损坏方式与 15/15-2 那一份同类**：**引用行与页名被逐字符错位 −0x1D**。例：第 1207 行把 `LoHa: can have the same number of trainable parameters but a higher rank and expressivity` 写成 `¨ : F D Q  K D Y H  W K H  V D P H  Q X P E H U  R I  W U D L Q D E O H  S D U D P H W H U V  E X W  D  K L J K H U  U D Q N`（按 +0x1D 解码逐字吻合）；第 457/535/509/1207/1332/5653 行同病。⇒ 我在这些行上**不下否定结论**，一律回到同一页的其它行或页号交叉确认。

## 结论

P0（事实错误）：**0** 条 ｜ P1（易误解/依据不足）：**3** 条 ｜ P2（措辞）：**6** 条

> P0 为 0 是我逐条回源后的结果，不是没查。本讲的高风险点（LoRA / QLoRA / QST / LoHa / LoKr / 前缀调优的归属）**逐条核完都对**，错误集中在「课件没说的数字」与「课件 outline 列了却没讲的一节」这两类。

## P0 · 事实错误

（无）

## P1 · 易误解或依据不足

1. **课件第 2 页有一整张任务对比表，本页正文与溯源都没有提。**
   - 课件第 2 页标题是 `LLMs Need Finetuning`，除本页引用的定义外，还有一张四任务表（第 56-123 行）：`SQuAD V2 (F1)` **69.8% → 88.4%**、`RTE (Acc)` **69% → 85.4%**、`WikiSQL (Acc)` **20% → 73%**、`Spider (Acc)` **18% → 62%**（列为 `GPT-3 Few-shot` 对 `GPT-3 Finetuned`）。
   - 本页溯源第 218 行自称「本讲取材范围分四块。**一是动机：微调的定义与全量微调的代价（八十块 A100-40GB、约 1 TB 存储）**」——它把第 2 页说成了只有定义，而课件把「微调带来大幅精度提升」放在成本**之前**。⇒ 读者会以为课件给出的动机只有成本。
2. **三个课件里根本没有的数字，被正文写成了事实。**
   - 位置：第 40 行「后面所有方法的共同目标，就是把这个「相同」变成**「百分之几」**」；第 80 行「于是可训练参数**从几十亿降到几百万**」（fig-5 的 `<desc>` 未含此数，只在正文）；第 94 行「适配器**只增加几 MB 的参数**」。
   - 我在源里检索 `illion`、`MB`、`fewer`、`trainable parameters`、`%`：课件全篇的数字只有 ① 第 2 页四个任务的准确率、② 第 3 页 `Eighty A100-40GB` / `One TB of data per checkpoint` / `Ten A100-40GB`、③ 第 23-24 页量化开销 `32/B`、`32/64=0.5 bits`、`8/64+32/(64*256)=0.127 bits`。**没有任何参数量、字节量、或「占全部训练成本的百分比」**。按方法 ③（数字必须回源，找不到记 P1）。
3. **「同一个主干可以配很多个适配器 / 按请求切换」——这是我们用自己的话补上了课件列了却没讲的一节。**
   - 位置：第 94 行「而适配器只增加几 MB 的参数，**同一个主干可以配很多个适配器**。这在多任务场景里省下的存储是成倍的」；第 122 行「LoRA 支持一件实践上很受欢迎的事：**同一个主干挂多份不同的低秩增量，按请求切换**」。
   - 课件 outline **四次**列出 `Serving adapters`（第 234/240 行页 4、第 602/608 行页 12、第 1305/1311 行页 21、第 1636/1642 行页 27），但**全篇没有这一页**；课件最后一页 `Recap: Efficient LLM Finetuning Methods`（第 4117-4176 行）里 `Serving adapters` **也已经消失**，只剩 `Prompt engineering / Prefix tuning / LoRA / QLoRA / Side tuning`。⇒ 课件没讲的这一节，正文用两处自有叙述补上了，而溯源第 219 行的三组推论里**没有**把这两处标出来。

## P2 · 措辞

1. **「课件还专门用一页讲「把 LoRA 用在注意力上」」**（第 108 行；`figures/llm-finetuning-7.svg` 第 28 行同句）—— 课件那一页（p17）同时有两块：`Apply LoRA to Attention` 与 **`Apply LoRA to MLP layer`**（第 962-976 行，图里并排列出 `Multi-Head Self Attention` 与 `ReLU` 的 MLP）。正文只提了 attention。紧随其后的理由「注意力那几层的投影矩阵本来就是这一层最值得调的部分」在课件里找不到，是我们的补充。
2. **「这一代 [[term:tensor-core]] 对低位宽格式的支持，正是这类技术能落地的前提」**（第 144 行）—— 课件量化那两页（p22-24，第 1317-1497 行）通篇没有提到硬件。
3. **「这一点把 LoRA 与「加一个额外分支」的做法区分开了 / 后者在推理时也要多走一次分支」**（第 120 行；`llm-finetuning-8.svg` 第 28 行）—— 课件 p18 标题是 `LoRA Does Not Increase Inference Latency`，它的对比是「带 LoRA 的训练时权重」与「并回后的 `Adapted Weight`」（第 1063-1165 行），**不是**「适配器 vs LoRA」。
4. **「它把「省可训练参数」和「省主干显存」两件事叠在了一起，于是单卡能微调的模型规模又上了一个台阶」**（第 172 行）—— 课件 QLoRA 三页（p25-26，第 1504-1577 行）只给「单个线性层：4-bit 冻结权重 / 16-bit LoRA 权重 / 16-bit 激活」与「`Achieves On-Par Performance as Full Finetuning`」，「单卡规模上一个台阶」不在课件文字层。
5. **溯源对第七项外部材料只写代称**（第 217 行）—— 其它六项都给了名字或标题（GPT-3、Cobus Greyling、Prefix-Tuning、Parameter-Efficient Transfer Learning for NLP 2019、LoRA Hu et al. 2021、QLoRA），最后一项写作「**以及量化侧调优那份工作**」，而课件给的是全名 `Quantized Side Tuning: Fast and Memory-Efficient Tuning of Quantized Large Language Models`（第 2180-2184、2664-2668、3129-3140、3442-3446 行）。七项的**计数没错**（我逐项核过，见下），只是命名不对称。
6. **「（思维链提示）它的效果在推理类任务上尤其明显，因为多步推理本身就需要模型把中间结果写出来」**（第 52 行）—— 课件 p8 只有 `Break a large task into sub-tasks and chain them together`（第 403-407 行），没有效果侧的说法。

## 判据 ⑧⑨⑩（这一轮新立的，逐条查）

**⑧ 两套并存的计数/编号体系 —— 课件自己有，本页只用了其中一套，且没说另一套。**

- 课件 `Tuning adapters` 这一支，**outline 列四项**（`LoRA` / `QLoRA` / `Side tuning` / **`Serving adapters`**，见 p4/12/21/27），**Recap 只剩三项**（`LoRA` / `QLoRA` / `Side tuning`，见第 4117-4176 行）。本页用的是 Recap 那一套（正文只讲 LoRA、QLoRA、侧调优），**没有说明 outline 里的第四项课件从未兑现**——而正文第 94/122 行恰好把它填上了（见 P1-3）。这既是 ⑧ 也是 ⑩ 的镜像（这里承诺来自课件自己，不是别的讲次）。
- 课件号与仓库讲次的错位本讲**不咬人**：本讲课件号 16 = 仓库讲次 17，但因为 `16-LLM-serving-2` 那一讲已经把错位吸收掉了，正文里的「上一讲」（第 56 行）指**第 16 讲 `llm-serving-2`**，而第 16 讲第 126 行确实在讲「把候选拆成多条序列会把键值缓存占用更多显存」⇒ 指代在内容上成立 ✅。（这与我在第 15/16 两讲报的同名问题不同，本讲是干净的。）

**⑨ 少认了源材料 —— 未发现硬命中，两条软的。**

- 溯源第 219 行把「把「不可微」说成提示工程的技术硬伤」列为我们的因果判断。课件自己就把这一点当成转折：第 430 行 `Not differentiable: cannot directly finetune on a given dataset`，紧接着第 433 行 `Can we make prompt trainable/differentiable?` ⇒ 课件本身已把它当成技术要点。
- 溯源第 219 行把「把「全量微调与从头训练同价」说成这一讲的动机」列为我们的因果判断。课件第 3 页的标题就是 `Finetuning LLMs is Extremely Expensive`、副标题 `Require same resources as training from scratch:`（第 132-137 行）⇒ 这是课件自己的论点。
- 归属写得**对**的地方（供对照）：`LoRA` 的定义句逐字来自第 784-786 行 `Freeze pretrained model weights and inject trainable rank decomposition matrices into each layer` ✅；`LoHa` 的「同参数量下秩更高」逐字来自被错位的第 1207 行（按 +0x1D 解出 `can have the same number of trainable parameters but a higher rank and expressivity`）✅；`LoKr`「保留原权重矩阵的秩」逐字来自第 1242 行 `Preserve the rank of the original weight matrix through Kronecker product` ✅；适配器出处「2019」来自第 727/757 行 `Parameter-Efficient Transfer Learning for NLP. 2019` ✅；`前缀调优` 的 `Prepend a sequence of virtual tokens` / `Freeze the LLM's parameters and finetune prefix parameters` 来自第 447-459 行 ✅；`QLoRA` 的 4/16/16 位来自第 1529-1555 行 ✅；`QST 两步`来自第 2646-2659、3107-3133、3405-3437 行 ✅；`与 QLoRA 精度相当而显存更省 / 用 GPT-4 当裁判`逐字来自第 3903-3921 行 ✅；`适配器省不掉激活值`逐字来自第 1665-1671 行 `Adapter networks reduce trainable weights and optimizer states / But require saving intermediate activations for back propagation` ✅。

**⑩ 跨讲承诺 —— 本讲对外 0 条承诺；incoming 0 条。**

- 本讲发给他讲的承诺：**无**（全篇没有「第 N 讲会讲透 X」这类句子）。
- 别人对本讲的引用：我在 `content/**/index.md` 全树检索 `第 17 讲`（以及 `微调` 的跨讲引用），**0 命中** ⇒ 没有别人许给本讲的承诺需要兑现。
- 本讲自己的跨讲引用逐条验过：第 56 行「上一讲」= 第 16 讲 ✅（见 ⑧ 节）；第 136 行「第 5 讲讲的『同一个形状配不同步长就是不同布局』」= 第 5 讲第 52-56 行「给行与列各存一个步长……行优先与列优先只是两组具体步长取值而已」✅；第 184/196 行「第 11 讲那条 O(N) 的显存开销」= 第 11 讲第 30 行小节标题「## 推理只要 O(1)，训练却要 O(N)」+ 第 38 行「训练一个 N 层的网络需要 O(N) 的显存」✅。

## 我核不到的（诚实记录）

- **「要把梯度从适配器回传到主干靠近输入的那几层」**（第 182 行）：课件 p28 只有「需要保存中间激活值」+ 一张 `LoRA for MLP layers` 的图（第 1653-1704 行），**没有**描述梯度的流向。我**不能**说这句对或错，也不能说它是课件说的。
- **课件 p29 与 p33 之间的显存对比图**（第 1706-2154、2188-2640、2672-3100 行等大量逐字符竖排的 `F u l l F u n t u n i n g 3 6 G B / 1 3 G B / 1 4 0 G B …`）：这是一张按字符竖排的表格/图，文本层只剩字母序列，**我无法可靠地把数字与标签配对**。⇒ 本页没有引用这些数，我也不对它们下结论（不排除「激活值显存」图上还有本页未用的依据）。
- **LoHa / LoKr 是否另有出处页**：课件把它们写成 `LoRA Variant 1 (LoHa)` / `Variant 2 (LoKr)`，**没有给引用行**（第 1181-1244 行区内没有 `*` 引用）。所以「课件在这一讲引了若干外部材料」的清单里不含它们；这不代表课件没引过它们的原始论文，只能说**在这一讲的可见文字里没有**。
- **Prompt 类插图内容**：第 7 页（`Prompt Engineering Techniques`）与第 8 页只有标题 + 图 + `Figure credits: Cobus Greyling`，图内文字不在文本层。

## 覆盖面

**配图（14 张 SVG，全部逐张通读：14/14）**：`llm-finetuning-1.svg` … `-14.svg` 逐张读过 `<title>`、`<desc>` 与全部 `<text>`（`desc` 不渲染，按方法 ⑦ 通读）。数字/名称逐项回源：`八十块 A100-40GB，约 1 TB 存储`（`-2.svg`）= 第 143-161 行 ✅；`LoHa 逐元素乘积，同参数量下秩更高` / `LoKr 克罗内克积，保留原权重的秩`（`-9.svg`）= 第 1181-1242 行 ✅；`FP32 转成 8 位整数`（`-10.svg`）= 第 1322-1345 行 ✅；`每块自己的常数，存在 FP32` / `把这些常数当作输入再量化一次`（`-11.svg`）= 第 1354-1429 行 ✅；`4 位冻住的主干 + 高精度的小矩阵`（`-12.svg`）= 第 1529-1555 行 ✅；`4 位分块双重量化` / `侧网络`（`-14.svg`）= 第 2646-2659、3405-3437 行 ✅；`这条正好接上第 11 讲`（`-13.svg`）✅。**图上未发现与源冲突的数字**；图上唯一与正文同源的问题是 `-7.svg`「专门讲了一页把 LoRA 用在注意力上」（P2-1）。
- 本讲配图图号（`-1` … `-14`）与课件页码（p1 … p33）是两套编号，本页没有混用（比第 15 讲干净）。

**源侧**：`mlsys-slide-16-LLM-finetuning.pdf.faithful.txt` 全 4,176 行用逐行读取方式过了一遍，其中**逐字精读**第 1-130、110-500、490-620、660-800、800-1180、1180-1430、1430-1800、2140-2200、2640-2700、3100-3160、3400-3470、3850-4176 行；其余行用**定向检索**覆盖，检索词与结果：`LoRA|LoHa|LoKr|QLoRA|Prefix|Adapter`（定位全部相关页）、`Serving|Side|activation|gradient|memory|GB`（定位第 2161/2643/3107/3405/3895 行，并**据此确认 `Serving adapters` 只出现在 outline、没有内容页**）、`illion|MB|%|fewer|trainable parameters`（定位全部数字）、`et al|http|redit|2019|2021`（定位全部引用行）。**没搜到 ≠ 不存在**：含 NUL 与错位行的位置我明确标了「不下结论」。

**正文侧**：`content/17-llm-finetuning/index.md` 220 行逐行读完；跨讲引用回源第 11、5、16 讲；`content/**/index.md` 全树检索 `第 17 讲` 确认无 incoming 承诺。
