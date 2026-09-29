# 事实核对 · CMU 15-442/15-642 第 16 讲 LLM 服务技术（下）：投机解码

- 核对人：非作者
- 核对日期：2026-09-29
- 被核对版本：`content/16-llm-serving-2/index.md`，归一化 SHA256 前16 = **F599743DE2075A03**
- 源材料（我实际依据的文件）：`_sources/mlsys-15442/evidence/mlsys-slide-15-LLM-serving-part2.pdf.faithful.txt`（36,999 B，6,416 行，**含 761 个 NUL 字节**，`read` 工具按二进制拒绝读取，改用逐行读取）；交叉讲引用另用 `content/14-llm-serving-1/index.md`、`content/15-blackwell-tirx/index.md`、`content/12-ml-compiler-data-layout/index.md`、`content/09-ml-parallelization-1/index.md`、`content/08-transformer-attention/index.md`、`content/11-memory-optimization/index.md`
- **⚠️ 拿对了源**：本讲的源是 `…-16-LLM-finetuning.pdf.faithful.txt` 之外的 **`15-LLM-serving-part2`**（仓库讲次 16 = 课件文件名 15）。第 17 讲才是 `16-LLM-finetuning`，两个「16-」不同名，本记录只依据 `15-LLM-serving-part2`。
- 抽取器与锚词（三步动作）：`faithful` 提取器；锚词 `SpecInfer`（命中）、`Speculative Speculative Decoding`（命中）、`LLAMA`（命中 `LLM: LLAMA-7B, SSM: LLAMA-160M`）、`Alpaca`（命中）。⇒ 锚词命中，可以继续用这一份。
- **★ 这份 faithful 有两类损坏，必须写在前面**：① **逐字符错位**（不像 eth-ca 那样整页丢，而是**零星几行的引用行**被按 −0x1D 错位）：第 2209 行把 `Speculative Inference and Verification. ASPLOS'24` 写成 `E D V H G  6 S H F X O D W L Y H  , Q I H U H Q F H  D Q G  9 H U L I L F D W L R Q .  $ 6 3 / 2 6 ¶ 2 4`；第 5637/6382 行把 `Today's Lecture: Speculative Decoding` 同样错位；第 1713/238/246 行把 `more/bottlenecked by` 那半句错位。② **kern 把词切成碎片**（`Fine` `-` `tuned` `SSM`、`Two` `-` `Tier` `Suffix`…）。⇒ 我**没有**在这些错位行上做否定判断；凡涉及被错位的句子，我都回到同一页的其它行或页号去确认。

## 结论

P0（事实错误）：**2** 条 ｜ P1（易误解/依据不足）：**6** 条 ｜ P2（措辞）：**5** 条

## P0 · 事实错误

| # | 位置 | 正文说 | 源材料说 | 依据（逐字引用 + 页码） |
| --- | --- | --- | --- | --- |
| 1 | `index.md` 第 215 行（溯源）与第 218 行（溯源） | 「课件在这一讲里引了若干外部工作……**SpecInfer、Medusa、Eagle 与 EAGLE-2、SSD、以及前瞻解码**」；第 218 行把它数成「本讲引的**五处**」 | 课件**有独立标题页**的外部工作至少 **7 处**，其中两处**本页正文自己也点了名** | 逐页核对：SpecInfer（第 701 行标题「SpecInfer: Tree-based Speculative Inference & Verification」+ 第 765 行 `* SpecInfer: Accelerating LLM Serving with Tree-based Speculative Inference and Verification. ASPLOS'24`）、Medusa（第 5459 行「Medusa: Speculative Decoding with Multiple Decoding Heads」，第 5466-5470 行 `https://www.together.ai/blog/medusa`）、EAGLE 与 EAGLE-2（第 5512/5518 行「EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty」/「EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees」）、SSD（第 5590/5609 行「Speculative Speculative Decoding (SSD)」，p34-35）、**Prompt Lookup Decoding（第 5680 行，p37）**、**SuffixDecoding: Two-Tier Suffix Tree Speculation（第 5690/6301-6303 行「SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications」，p38）**、Lookahead Decoding（第 6312/6353 行「Break the Sequential Dependency of LLM Inference Using Lookahead Decoding」，p43-44）。而正文第 180 行**就写了**「Prompt lookup 直接从提示词里查……SuffixDecoding 用两级后缀树来做投机」⇒ 溯源漏掉的两个恰是正文写了的两个。若按「篇」数，EAGLE 与 EAGLE-2 是两篇，则更多 |
| 2 | `index.md` 第 186 行、第 198 行 | 第 186 行「**课件最后**指出一个容易被忽略的问题」（指 SSD）；第 198 行「**课件的这一页之后，这一讲就结束了**」 | SSD 是 **p34-35**，后面还有 9 页：p36 是分隔页、p37 Prompt Lookup Decoding、p38 SuffixDecoding、p43-44 Lookahead Decoding，**课件的最后一页又是** `Today's Lecture: Speculative Decoding` | 页号印在幻灯片上，逐页可见：第 5597 行 `34`、第 5625 行 `35`（都在 SSD 页内）、第 5671 行 `36`（`Today's Lecture: Speculative Decoding` 分隔页）、第 5682 行 `37`（Prompt Lookup Decoding）、第 5690-5698 行 SuffixDecoding（`5` `8` = 38）、第 6350 行 `43`、第 6370 行 `44`（Lookahead Decoding 两页）、第 6377-6416 行为全篇最后一页（`Today's Lecture: Speculative Decoding` + `Model-based / Model-free speculative decoding`）。⇒ 课件"最后"讲的是 model-free 三条路线里的 Lookahead，不是 SSD |

## P1 · 易误解或依据不足

1. **「这个取舍和上一讲讲的「复制还是切分」是同一类」**（第 104 行；溯源第 217 行「把草稿来源的取舍与上一讲的复制与切分归为同一类」）
   - 全仓库检索 `复制还是切分` / `复制与切分` **只命中本页这两处**；在 `14-llm-serving-1/index.md` 里检索 `复制|切分` **只有一条无关命中**（第 232 行「两份 PDF……因此没有做切分」）。「切分 vs 复制」这个二分法实际出现在**第 9 讲**（`09-ml-parallelization-1/index.md` 第 42 行「## 数据并行：切数据，复制模型」）与**第 12 讲**（`12-ml-compiler-data-layout/index.md` 第 108 行「## 复制：不是切开，而是各留一份」，第 116 行「切分意味着每块设备只有一部分……复制意味着每块设备都有完整的」）⇒ **上一讲没有这个二分法**，「上一讲讲的」无所指。
2. **「课件给的三档参数量是 1750 亿、130 亿、27 亿」**（第 50 行）
   - 源里那一页（标题 `Tradeoffs between Different Language Models`）给的是**五档**：第 364/367/370/373/376 行 `175B` / `13B` / `2.7B` / **`760M`** / **`125M`**，后两档还各带 TriviaQA / PIQA / SQuAD / latency / #A100s 五列数值（760M 的 latency 1.1s、125M 的 0.3s）。⇒ 「三档」少认了两档（且正文没说这是节选）。同一句「差了近两个数量级」用 175B 对 2.7B 是成立的。
3. **「把大模型微调成小的」当作四种来源之一**（第 102 行）
   - 源（`Small speculative models` 那一页，第 1031/1046/1052/1058-1068 行）给的四个标签逐字是 `Quantized LLM`、`Distilled LLM`、**`Fine-tuned SSM`**、`Speculator`。第三项是「微调一个 **SSM**」，与「把大模型微调成小的」是两种不同的做法。四项的**计数是对的**，第三项的名称被换成了另一种方法。
4. **「第 15 讲讲的「由静态到动态」的演进，在这里又出现了一次」**（第 172 行）
   - 本页 `source_url` 是 `slides/15-LLM-serving-part2.pdf`、front matter 是 `lecture = 16` ⇒ 本讲的**课件号是 15、仓库讲次是 16**。两种读法都不成立：若「第 15 讲」按仓库讲次 = `15-blackwell-tirx`，该讲正文与源里**没有**「由静态到动态」这条演进线（见 L15 记录 ⑩ 节）；若按课件号，则「第 15 讲」就是**本讲**，句子变成自指。⇒ 指代不明，且两种解释都读不通。
5. **「上一讲」×4 的指代**（第 20、104、128、217 行）
   - 四处都指**第 14 讲**（part 1）的内容：第 20 行「很多请求怎么排、缓存怎么放」= 第 14 讲的连续批处理与 PagedAttention；第 128 行「上一讲刚解决好的显存问题」= 第 14 讲的 KV 缓存显存；溯源第 218 行自己写明了「本讲与第 14 讲的关系」。但按仓库讲次，**上一讲是第 15 讲 `blackwell-tirx`**（讲 Blackwell/TIRx，与本页四处内容都无关）。⇒ 建议正文一律写「第 14 讲」。（同一问题我在第 15 讲也报了：L15 第 70 行「上一讲的描述符」。）
6. **SpecInfer 收益区间的成因**（第 88 行）：「这个区间的上界与下界也说明了投机的收益不稳定：它取决于任务里前缀的重复程度、以及草稿模型与目标模型的接近程度。」
   - 源在同一页（第 722-746 行）只给结论：「Better performance: outperform existing LLM systems by `1.3`-`2.4x`」与「Higher efficiency: reduce GPU memory access by `2.5`-`4.4x`」，**没有**对区间成因的解释。我在源里检索 `prefix`、`depend`、`task`、`varies` 也没找到。⇒ 这条归因无可依据（也不是溯源里列出的那几条「推论」之一）。

## P2 · 措辞

1. **「不基于模型的，用输入本身里的重复去猜」**（第 24 行）、**「它在输入里有大量重复时特别有效」**（第 184 行）—— 课件对 model-free 的逐字定义是「`Using previously generated tokens to predict future tokens`」（第 5669/6414 行），也就是**用已经生成的 token**，不是「输入本身里的重复」。两者在大方向上相邻，但这句是把课件自己的类别定义translate 成了另一个说法。
2. **「这个例子里「三个」这个数字很有代表性。它不是随机的，而是取决于小模型猜得准不准、以及大模型愿意一次验证多少个候选」**（第 76 行）—— 源只写「`Generate 3 new tokens in one LLM decoding step`」（第 642 行），没有「不是随机的」这类判断，也没有出处。
3. **「课件用一页说明，最朴素的采样做法可能是次优的」后被复述成「如果只是「大模型说这个 token 概率高就接受」」**（第 152、154 行）—— 课件那一页的 strawman（第 2729-2767 行）是「`A strawman approach: naïve sampling` → `Use LLM to sample` → `Verify if [token] is in the token tree`」，紧接着第 2939 行（错位行）标注 `naïve sampling's verification proc. = 50%`、第 2949 行 `= 100%`（直接接受 SSM 2 时）。本页把 strawman 换成了「按大模型概率高就接受」，与课件的反例设定不是同一个规则。
4. **「这一段是这一讲技术含量最高的部分，也是**唯一一处**涉及概率推导的地方」**（第 160 行）—— 课件在令牌树那几页（第 812-1011 行）通篇标的是概率比 `P4`/`P5`/`P6`/`P7`/`P8`，在朴素采样那页（第 2825-2899 行）给的是 `0.25`/`1.0`/`50%`/`100%`。「唯一一处」过强。
5. **「课件给的例子是一次大模型解码步骤里生成三个新 token」后接「课件的演示把这一次前向的结果画得很直观：三个位置同时被算出概率，然后从左往右逐个判断是否与草稿一致，遇到第一个不一致的地方就停下。停下之后，后面那些位置算出来的结果就被丢弃了」**（第 78 行）—— 「遇到第一个不一致就停下、后面的丢弃」这句**在文本层里找不到**（那一页是示意图/动画，文字层只剩 `SSM Predictions` / `LLM Outputs:` / `Verified output: machine learning system optimization`）。这属于我对源的可核范围之外，但正文用了「课件的演示把……画得」这种**归属句式**，建议改成无归属的说明。

## 判据 ⑧⑨⑩（这一轮新立的，逐条查）

**⑧ 两套并存的计数/编号体系 —— 本讲是重灾区，且正文没有区分。**

- 课件的文件名/页码体系与仓库的讲次体系**错开一位**：本讲 `source_url` = `slides/15-LLM-serving-part2.pdf`（课件号 **15**），front matter = `lecture = 16`（仓库讲次 **16**）；同理第 14 讲 = 课件 14 = 仓库 14。这是因为仓库在两者之间插了 `15-blackwell-tirx`（课件是 Week 9 的网页版，无 PDF 编号）。
- 正文没有说明这件事，于是同时出现三种危险写法：第 172 行「第 15 讲」（到底指哪个体系？两读都错，见 P1-4）、第 20/104/128/217 行「上一讲」（按内容指第 14 讲，按讲次是第 15 讲）、第 218 行「第 14 讲引的三处外部材料与本讲引的五处」（第 14 讲那 **3** 处我核了：`14-llm-serving-1/index.md` 第 229 行 = Orca / vLLM / SGLang，✅ 对；本讲的「五处」✗ 见 P0-1）。
- **建议**：在本页首次出现处写一句「本讲对应课件 `…-15-…`（课件编号与仓库讲次差一位）」，并把「上一讲」全部改写为「第 14 讲」。

**⑨ 少认了源材料 —— 未发现硬命中，只有两条软的。**

- 溯源第 217 行把「指出「结果相同」意味着不改变输出分布」列为我们的「结构上的观察」。源里有两处近乎同义的原句：第 754-762 行 `Correctness: verification guarantees end-to-end equivalence`、第 2019 行 `same output as sequence attention for each token; no redundancy`。⇒ 这条「观察」的**半边是课件的原话**（end-to-end equivalence），正文第 144 行也老实写了「「结果相同」这句话也很重要」。
- 溯源第 217 行把「把「瓶颈是读权重」推成「判断投机值不值要看猜中比例」」列为我们的「判断」。课件自己在朴素采样那页就把结论量化成了验证概率（`naïve sampling's verification proc.` 50% 对 100%，第 2939/2949 行）⇒ 「看猜中比例」这条课件的方向是一致的，不算纯属我们补的。
- 反例（归属写得**对**的地方，供对照）：第 116 行「这个结构在第 14 讲出现过一次：RadixAttention 用一棵基数树」—— 第 14 讲第 188 行确有「用一个基数树，也就是紧凑前缀树」✅；第 118 行「第 8 讲的 Flash-Decoding」—— 第 8 讲第 184 行确有「## Flash-Decoding：改从键值这一侧切」✅；第 106 行「大模型用 LLAMA-7B、小模型用 LLAMA-160M、数据集是 Alpaca、显卡是 A10」✅ 与第 1236-1244 行逐字一致；第 66 行「第 11 讲的检查点间隔」—— 第 11 讲确有「## 检查点：只把一部分留下」✅。

**⑩ 跨讲承诺 —— 本讲对外 0 条承诺；别人对本讲的引用都落在关系声明上。**

- 本讲发给他讲的承诺：**无**（第 144 行「这一点后面讲采样时还会再回到」指本讲内部，且确实在第 146 行之后兑现）。
- 别人对本讲的引用：第 14 讲 `14-llm-serving-1/index.md` 第 232 行「本讲与第 16 讲的关系：两份 PDF 是各自独立的课件（part1 与 part2），页码各自从 1 开始，内容也不重叠，因此没有做切分」——与本讲溯源第 218 行的说法**两侧一致** ✅（并且这也解释了为什么本讲页码从 1 开始）。
- 唯一未兑现方向是本讲自己写出的 **P1-4「第 15 讲」**：本讲承诺读者去第 15 讲找「由静态到动态」，而 `15-blackwell-tirx` 没有这条线。该条已同时记入第 15 讲的记录（⑩ 节），**两讲的记录互为证据**。

## 我核不到的（诚实记录）

- **「遇到第一个不一致的地方就停下」**（第 78 行）：涉及的那几页（p9-p12）在文本层里只有矩阵与概率标签，动画语义不在文本层 ⇒ 我**不能**说它对或错。
- **Prompt Lookup Decoding 的做法描述**（第 180 行「如果输入里刚出现过同样的片段，就直接把后面那一段抄过来当草稿」）：课件 p37 **只有标题**（第 5680 行），正文内容在图片里，文本层无依据 ⇒ 只能记「课件未给文字依据」，不能说错。
- **「三个 token 不是随机的」**（第 76 行）：见 P2-2，源无此判断。
- **未使用的中途数字**：源里还有 `Compute Resources* / Memory Bandwidth* / 76% / 2%`（第 305-318 行，注 `* Measured by serving LLAMA-2 70B on 4 A100 GPUs with 4K sequence length`）与 `2.5-4.4x reduce GPU memory access`、`latency 20s/7.6s/2.7s/1.1s/0.3s`、`#A100s 10/1/1/1/1`、`TriviaQA/PIQA/SQuAD` 三组分数，本页都**没有引用**，所以它们不构成正文的错误；**但我也没核出哪个 76% 配哪个标签**（文本层给不出 x 坐标，两个标签在前、两个数值在后），这条只作为「源里有、本页没用」记录。
- **错位行上的主张**：第 769/2209/5637/6382 行的引用与页名是被算子错位的（−0x1D），我是**用同页相邻行**（第 765、5615、5671 行等）交叉确认的，没有在错位字节上直接下结论。

## 覆盖面

**配图（14 张 SVG，全部逐张通读：14/14）**：`llm-serving-2-1.svg` … `-14.svg`。数字类逐项回源结果：`1.3 到 2.4 倍`（`-6.svg`）= 第 727-731 行 `1.3`-`2.4x` ✅；`1750 亿 / 130 亿 / 27 亿`（`-3.svg`）= 第 364/367/370 行 `175B/13B/2.7B` ✅（但源的完整列表是五档，见 P1-2）；`一个 LLM、两个 SSM、四个 token`（`-11.svg`）= 第 2782 行 `Assume one LLM, two SSMs, and four possible tokens:` ✅；`三个 token`（`-4.svg`/`-5.svg`）= 第 642 行 `Generate 3 new tokens in one LLM decoding step` ✅；`SSM`（`-4.svg`）= 第 646 行 `SSM Predictions` ✅（且第 1236-1244 行的实验设置把 SSM 展开成 LLAMA-160M）；`树拓扑感知的因果掩码 / 深度优先线性化`（`-10.svg`）= 第 2142-2156 行 `A DFS-based approach to linearizing a token tree` / `Tree topology-aware causal mask` ✅；`四组来源`（`-7.svg`）= 第 1046-1068 行四个标签 ✅（第三项名称见 P1-3）；`Prompt lookup / SuffixDecoding / Lookahead 三条`（`-13.svg`）= 第 5680/5690/6312 行 ✅；`Speculative Speculative Decoding (SSD)`（`-14.svg`）= 第 5590 行 ✅。**图上没有发现新的与源冲突的数字。**
- **注意**：本讲配图的图号（`-1` … `-14`）与课件页码（p1 … p44）是两套编号，本页没有在一处混用（这一点比第 15 讲干净）。

**源侧**：`mlsys-slide-15-LLM-serving-part2.pdf.faithful.txt` 全 6,416 行用逐行读取方式过了一遍，其中**逐字精读**第 230-300、358-470、630-1030、1031-1260、1680-1830、2195-2215、2700-3160、3143-3160、5400-5710、6300-6416 行；其余行用**定向检索**覆盖，检索词与命中：`SpecInfer|Medusa|Eagle|SSD|Lookahead|Suffix|Prompt`（命中见 P0-1）、`attention|mask|DFS|topolog|redundan|sequential`（定位第 2013/2019/2142/2156/1705 行）、`sampling|accept|reject|distribution|big model|two small|four`（定位第 2731/2778/2782/2992/3058/3132 行）、`[0-9]+x` 类数字。**没搜到 ≠ 不存在**：含 NUL 与错位行的位置我明确标了「不下结论」。

**正文侧**：`content/16-llm-serving-2/index.md` 218 行逐行读完；跨讲引用逐条回源：第 14 讲（`复制|切分`、`瓶颈|权重`、`RadixAttention|基数树`）、第 15 讲（`blackwell-tirx/index.md` 全篇 + 检索 `静态|动态`）、第 12 讲（`复制`）、第 9 讲（`复制|切分`）、第 8 讲（`Flash-Decoding`）、第 11 讲（`检查点`）。
