# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 13 讲 ML 编译器（下）：现代 GPU 上的 GEMM

- 核对人：**非作者**（独立核对；作者 `mlsys-author` 未参与，未提问、未改正文）
- 核对日期：2026-09-29
- 被核对版本：`content/13-ml-compiler-gemm/index.md`
  归一化 SHA256 前16 = **E283D1CD9A2280D1**（19,635 B）
  - 14 张配图（哈希入档，例：`-5 17E7FBB0A7E1632D`、`-10 316231542C928FD3`、`-12 44782A46626129AB`）
- 源材料：

| # | 文件 | 用途 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-deck-gemm.html`（6,883 B，主页面） | 四条 outline、12 个 `<iframe>` 的清单 |
| 2 | `evidence/gemm/swizzle_atom_128b.html`（17,765 B） | **`swizzled_col = logical_col XOR row`**、原子 = 8 行 × 8 扇区列 = 8 × 128B |
| 3 | `evidence/gemm/tensor_core_shapes.html`（12,071 B） | **M/N 四档、K 固定 16、Transpose A/B** |
| 4 | `evidence/gemm/tensor_core_to_swizzle.html`（15,999 B） | M×16 读取、一个 8×8 = 8×16B 格、2×2 个 8×8 小块 |
| 5 | `evidence/gemm/why_128b.html`（6,954 B） | **两侧各一条理由**、`unless tile width < 64 fp16` |
| 6 | `evidence/gemm/tiling_exploration.html`（17,750 B） | 分块 + swizzle 的探索页、四种格式 |
| 7 | `evidence/gemm/tma_copy.html`（12,091 B） | 2D TMA、`16×128 fp16`（每格 16B=8 fp16）、`cp.async.bulk tensor.2d + SWIZZLE_128B` |
| 8 | `evidence/gemm/tma_3d.html`（12,766 B） | 3D TMA、`16×256 fp16 (contiguous, row = 512B)` |
| 9 | `evidence/gemm/gemm_workflow.html`（5,868 B） | 四步工作流与三条 constraint |
| 10 | `evidence/gemm/gemm_endtoend.html`（13,267 B） | 端到端通路、**N block / Outer K / Inner K 三级控制**、B 路径省略 |
| 11 | `evidence/mlsys-webrepo-tree.txt` L140–166 | 该目录**实际有哪些** demo 页（判断覆盖面用） |
| 12 | `evidence/mlsys-slide-06-CUDA-programming.pdf.faithful.txt`（第 1751 行起） | 核 L112 的跨讲归属（协作加载） |

> 定位方式：**幻灯片标题 + 逐字原文**（源是 HTML 全文，无换页符问题）。主页面本身几乎只有标题 ——
> 全部说明文字都在那 12 个 `demo/` 页里。

---

## 结论

**P0（事实错误）：1 条 ｜ P1（易误解/依据不足）：1 条 ｜ P2（措辞）：2 条**

---

## P0 · 事实错误

### P0-1 正文 L172 与图 12「课件还标出了**两重**循环」——源页把 K 拆成 **Outer K 与 Inner K** 两级（加 `N block` 共**三**级）；随之而来的「K 每一轮都要换一块新的 A 和 B」只对 **Outer K** 成立

- **正文 L172**：「课件还标出了**两重循环**：外层是 **N 方向的分块**，内层是 **K 方向的分块**。
  这两重循环也解释了为什么共享内存要反复被填：**K 方向的每一轮都要换一块新的 A 和 B**，而这个填充动作就是 TMA 的工作。」
- **配图 `ml-compiler-gemm-12.svg`**（可见文字 L28–29）：「课件还标出了**两重循环** / 外层是 N 方向的分块，
  内层是 K 方向的分块」——与正文同一处说法（`desc` 里没有这句）。
- **源（`gemm_endtoend.html`）逐字**：三组控件，标签分别是
  ```
  <span class="lbl">N block</span>    → 0, 1                      （N_TILES = 2）
  <span class="lbl">Outer K</span>    → 0, 1                      （K_TILES = 2）
  <span class="lbl">Inner K</span>    → 0..7                      （INNER_K = SMEM_B = 8）
  ```
  以及运行期的状态行与步进函数：
  ```
  'N block ' + ST.nBlock + '/' + N_TILES + ' | K step ' + absK + ' of ' + TOTAL_K +
    ' (outer K=' + ST.outerK + ', inner K=' + ST.innerK + ')'
  function globalStep() { return ST.nBlock * TOTAL_K + ST.outerK * INNER_K + ST.innerK; }
  var TOTAL_K = K_TILES * INNER_K;   // 2 * 8 = 16
  ```
  ⇒ 步进是 **N block × Outer K × Inner K** 三层嵌套（`globalStep` 里三个乘加项），不是两层。
- **第二半句为什么不成立**：源里 TMA 的搬运只挂在 **Outer K** 上 ——
  `TMA: A[nStart*16 : nEnd*16, kSmemStart*16 : kSmemEnd*16] → smem`，其中
  `kSmemStart = ST.outerK * SMEM_B` 只随 **outer K** 变；而 **inner K** 的 8 步是在**同一块已搬进来的 128×128 共享内存分块**里
  逐列前进（`Asmem` 那一格里高亮的是 `c === ST.innerK` 的那一列，`TensorCore: K=absKGlobal*16–+15`）。
  ⇒ 「先搬一整块 128×128、再在里面做 8 次 K=16 的小步」正是这一页的结构；把两级 K 合并成「内层是 K 方向的分块」后，
  「K 方向的每一轮都要换一块新的 A 和 B」会让读者以为 16 轮 K 每轮都重新填充共享内存（实际只有 **2** 次填充 / 每个 N 分块）。
- **为什么算 P0**：这是一条**关于源页结构的计数**（与前几轮「收成四个词、源列的是五个」同一类），
  而且它紧接着的那句因果（每轮重新填充）与源的数据通路相反；语句本身读起来毫无破绽。
- **建议修**：改成「课件标出了**三层**循环：N 分块、K 方向的**外层**分块（每轮 TMA 搬一整块 128×128 进共享内存）、
  以及小块内部的 **inner K** 小步（在已就位的共享内存里走 8 次 K=16）」；图 12 的可见文字同步改。

---

## P1 · 易误解或依据不足

### P1-1 溯源 L215 的「它嵌入的**九个**说明页面」——主页面实际嵌入 **12** 个 iframe，缓存清单里少了 3 个

- **溯源 L215 原文**：「本页用到的依据有两部分：一是课件主页面的小节标题与文字段落；二是它**嵌入的九个说明页面**，
  分别是张量核心的形状、张量核心与 swizzle 的关系、TMA 的二维拷贝、三维 TMA、为什么偏好 128B、GEMM 的优化工作流、
  端到端 GEMM、SWIZZLE_128B 的原子、以及分块与 swizzle 的探索页。两部分的原文都缓存为本地的 HTML 文件……」
- **源主页面 `mlsys-deck-gemm.html` 里的 `<iframe>` 共 12 个**（L52/60/68/76/84/103/111/130/138/157/165/173）：
  `swizzle_8x8`、`swizzle_128B`、**`swizzle_atom_128b`**、**`swizzle_atom_general`**、**`tiling_exploration`**、
  **`tensor_core_shapes`**、**`tensor_core_to_swizzle`**、**`tma_copy`**、**`tma_3d`**、**`why_128b`**、
  **`gemm_workflow`**、**`gemm_endtoend`**（粗体 = 溯源里那 9 个，也确实都在 `evidence/gemm/` 里缓存了）。
- ⇒ **未缓存 / 未列入的 3 个**：`demo/swizzle_8x8.html`（16,862 B）、`demo/swizzle_128B.html`（18,936 B）、
  `demo/swizzle_atom_general.html`（21,880 B，是「Swizzle Atoms: All Formats」那一页的载体）——
  三份都在主页面的嵌入清单里（`mlsys-webrepo-tree.txt` L120/146/150）。
- **影响面**：本页**没有**哪一句只依赖那三页（L36 的 8×8 XOR 机制在 `swizzle_atom_128b.html` L95/L147 与
  `tiling_exploration.html` L368 里都有；L138 的「很多种格式」在 `why_128b.html` 的 `FORMATS` 数组里就有 ✅），
  所以这不是内容错误；但「九个」这个**计数**与主页面的 12 个 iframe 对不上 —— 又是规则⑧那类「计数只说了一套」。
- **建议修**：改成「主页面嵌入的 12 个 `demo/` 页里，本页用到了 9 个（逐字比对，全部缓存）；另 3 个
  （`swizzle_8x8`、`swizzle_128B`、`swizzle_atom_general`）未取到，本页未复现」。

---

## P2 · 措辞

### P2-1 正文 L72 与图 5 把源的约束写成「分块尺寸必须能被 swizzle 原子**整除**」，比源更含糊，且漏掉源给的补救做法

- **正文 L72**：「你选的共享内存分块尺寸必须能被 swizzle 原子**整除**，否则重映射会把一批地址映射到块外去。」
  **图 5** 可见文字 L23/L26：「约束是什么 / 分块要能被 swizzle 原子整除」「为什么 / 否则重映射会跨出块外」。
- **源（`gemm_workflow.html` 第 3 步）逐字**：
  ```
  title:      '3. Tile Shared Memory Based on Swizzle Constraint'
  subtitle:   'Inner tile width must match swizzle atom width'
  constraint: 'If tile wider than atom, split into groups'
  detail:     'If shared memory tile is wider than 64 fp16, tile into groups of atom-width columns.'
  ```
  ⇒ 源的约束挂在**内层分块宽度**上（必须与原子宽度匹配），并且明确给出补救：**比原子宽就按原子宽度切成 groups**。
  页面的「分块尺寸能被原子整除」把约束范围放大了（听起来对整个分块形状都成立），也把源的「切 groups」这一步吞掉了。
  内容不算错（整除是同一件事的另一种说法），但比源含糊。建议照源写「**内层**分块宽度要与原子宽度对齐；比原子宽就按原子宽度切成若干 group」。

### P2-2 四处「机制级展开」是页面补的，溯源 L217 的推论清单没有列

| 位置 | 页面说 | 源里有的 |
| --- | --- | --- |
| L150 | 「64 个 fp16 **正好是 128 字节**……否则按 128B 的模式去搬，每一行都会读进用不到的字节，多出来的部分反而浪费带宽」 | `SWIZZLE_128B gives 128 contiguous bytes per row — the best default unless tile width < 64 fp16`（**没有**「浪费带宽」这个理由，也没有 64 fp16 = 128B 这一步换算；数字 64 与 128 本身都在源里 ✅） |
| L176 | 「因为 TMA 是**异步**的，填下一块与算当前块可以**重叠**」 | `gemm_endtoend.html` 只有 `In smem (waiting)` / `Consumed` 两个状态与 `mbarrier::complete_tx::bytes`，**没有**重叠这句话 |
| L100 | 「所以『无冲突』必须对**每一个小块**都成立，这也是**原子尺寸不能随意缩小**的原因」 | `tensor_core_to_swizzle.html` 只有 `2×2 of 8×8` 与 `each 8×8 is a 8×16B cell, conflict-free if swizzled`（**没有**「所以不能缩小」这条推论） |
| L64 | 「异或两次就还原」「可逆性是它能做成**组合逻辑**的前提」 | 源以代码体现可逆（`sector` 与 `logAtPhys` 互为逆），正文里**没有**这句文字 ⇒ 溯源已声明「廉价性归因于组合逻辑」，但「异或两次就还原」未列入 |

⇒ 溯源 L217 目前列了 6 条推论；以上 4 处按同一标准也应补进去（内容本身多数成立，**不必删**）。

---

## 已核对通过（逐条附幻灯片标题 + 逐字引用）

> ★ 本讲被点名的高危三处**全部逐字核到**：

| 正文 | 源 | 结果 |
| --- | --- | --- |
| **L60「课件的写法是 `swizzled_col = logical_col XOR row`」** | `swizzle_atom_128b.html` 页眉标签：`swizzled_col = logical_col XOR row`；实现 `const sector = (r,c,sw) => sw ? (c^r) : c;` | ✅ **逐字**（`c^r` = col XOR row） |
| **L62/L64 为什么用异或、为什么可逆** | 同页 `logAtPhys = (r,p,sw) => sw ? (p^r) : p`（`sector` 的逆）；`With Swizzle (XOR)` 面板 + 逐周期读演示 `1 cycle — all 8 sectors used simultaneously`（`c^r` 对固定列给出 8 个不同值） | ✅ 机制对；「异或两次就还原」是页面自己的说法（见 P2-2） |
| **L84 M/N 四档、K 固定 16、两个转置开关** | `tensor_core_shapes.html`：`Transpose A`（No/Yes）、`Transpose B`（No/Yes）、`M (output rows)` → 16/32/64/128、`N (output cols)` → 16/32/64/128、`K` → **单个 `disabled` 的按钮 `16`**；公式串 `'MMA m' + ST.n + 'n' + ST.m + 'k16'` | ✅ **四处全对**（含 `K` 的按钮是 disabled 的 16） |
| **L86「K 固定为 16 意味着每次要摆出来的都是 16 列」** | `tensor_core_to_swizzle.html` 副标题：`Tensor core reads M×16 tile from shared memory`；`tensor_core_shapes.html` 的 `MMA …k16` | ✅ 逐字 |
| **L142 为什么默认 128B：两侧各一条理由** | `why_128b.html`：`From tensor core side: any swizzle format works (16×16 tile decomposes into any atom size).` / `From global memory side: each atom row is a contiguous segment. Wider row = fewer, larger reads = better bandwidth.` | ✅ **两侧各一条，逐字** |
| **L144 结论与限定条件** | 同页：`SWIZZLE_128B gives 128 contiguous bytes per row — the best default unless tile width < 64 fp16.` | ✅ **逐字**（含 `64 fp16` 这个限定） |
| L24 大纲四条：swizzle 深入 / 张量核心 / TMA / 拼起来 | 主页面 `Outline`：`Swizzle Deeper Dive` / `Tensor Cores` / `TMA (Tensor Memory Accelerator)` / `Putting It Together` | ✅ 逐字 |
| L48 原子 = 8 行 × 8 个扇区列 = 8 × 128B；「把一个扇区里的所有 bank 缩成一格」 | `swizzle_atom_128b.html` 副标题：`8 rows, 8 sector columns, 8 bank sectors total (note: we are just collapsing all banks in a sector into a single cell)` + 标签 `Atom = 8 rows × 8 cols = 8 × 128B` | ✅ 逐字（含那条 note） |
| L52 一个扇区由若干 bank 组成，缩成一格不改变地址计算 | 同页 note；`why_128b.html` 图例 `1 cell = 16 bytes = 1 bank sector` | ✅ |
| L94 张量核心读 M×16，需要一次 8×8 无冲突 | `tensor_core_to_swizzle.html` 副标题：`Tensor core reads M×16 tile from shared memory — benefits from 8×8 conflict-free read that swizzle guarantees` | ✅ 逐字 |
| L96「这个 8 乘 8 就是 8 个 16 字节的格」 | 同页 `zoom-note`：`each 8×8 is a 8×16B cell, conflict-free if swizzled` | ✅ 逐字 |
| L100 源把 A 的分块画成 2 乘 2 个 8 乘 8 小块 | 同页默认态：`<div class="dims" id="zd">2×2 of 8×8</div>`（M=16 ⇒ `nBlocks*2 × 2`） | ✅（**2×2 是默认档 M=16 下的样子**；改 M 会变，正文按默认档说，成立） |
| L108「TMA 是带可选 swizzle 的硬件二维拷贝，一条指令，不需要线程」 | `tma_copy.html` 副标题：`Hardware 2D copy with optional swizzle — one instruction, no threads` | ✅ 逐字 |
| L114 指令写法 `cp.async.bulk tensor.2d` + `SWIZZLE_128B` | 同页：`cp.async.bulk<br>tensor.2d<br>+ SWIZZLE_128B`；完整形式 `cp.async.bulk.tensor.2d.shared::cta.global…` | ✅ |
| L120 `16×128 fp16`，每格 16 字节 = 8 个 fp16；出来是 8×8 扇区 | 同页：`16×128 fp16 (each cell = 16B = 1×8 fp16)` → `8×8 sectors (swizzled)` | ✅ **三个数全对** |
| L128 `16×256 fp16`，每行连续 **512 字节** | `tma_3d.html`：`16×256 fp16 (contiguous, row = 512B)`；`ROW_BYTES = 512;   // 256 fp16 × 2B` | ✅ **逐字**（含 512） |
| L130 3D TMA 一次完成「按块切」与「按模式重排」 | 同页副标题 `Use 3D TMA to copy into tiled shared memory` + 共享内存面板标题 `Shared Memory (tiled & swizzled)` | ✅ |
| L158 四步：选分块形状 → 定 swizzle → 按约束回头调分块 → 配 TMA | `gemm_workflow.html`：`Tiling shape → Best swizzle → Swizzle-constrained tiling → TMA with swizzle` + 四个 `STEPS[].title` | ✅ **四步逐条对应** |
| L160 次序不能颠倒（第三步回头改分块会让 TMA 配置重做） | 同页 `sub: 'From shared memory tiling to TMA data movement'` + 详情栏 `Design shared memory layout first, then configure TMA to fill it efficiently.` | ✅ 方向对（「配置重做一遍」是页面的展开，见溯源已声明的「归因于第三步的回调」） |
| L170 通路：TMA 搬进共享内存、张量核心读出两块做乘加、写进 C；B 的路径省略 | `gemm_endtoend.html` 副标题 `Data path: TMA loads tiles into shared memory, TensorCore reads for compute` + 页脚斜体 `B loading path (global → shared memory) omitted for simplicity` + 面板 `A (global memory) → TMA → A (shared memory) × B (shared memory) → TensorCore → C` | ✅ 通路逐字（**省略的理由**见下） |
| L112「第 6 讲讲协作加载时，『谁搬哪一块』是要手工安排的细节」 | **第 6 讲** faithful 第 1751 行：`All threads cooperatively load` + `global into shared memory`（一维卷积第二版）；另见第 6 讲正文 L159「一个 warp 是 32 个线程」 | ✅ **归属成立**（注：第 7 讲另有一个同名小节 `## 协作加载`（矩阵乘共享内存分块），两处都讲；页面未区分指哪一处 —— 只是提示，不计为发现） |
| L174 这个权衡与第 5 讲的分块、第 8 讲的分块尺寸同类 | 本仓库编号：05=optimizing-linear-algebra（分块）、08=transformer-attention（分块尺寸；第 11 讲 L70 也这么记） | ✅ 两处归属一致 |
| L190「第 20 讲要讲的内核超优化」 | 仓库存在 `content/20-kernel-superoptimization/`；第 21 讲 L110 亦按同一编号回指第 12/13 讲 | ✅ |

**跨讲承诺（规则⑩）**：
1. **本讲兑现了第 12 讲给它的承诺** —— 第 12 讲 L192「第 13 讲会看到这套记号怎么用在 GEMM 上」，
   本讲 L192–196 有专节 `## 这一讲与第 12 讲的关系`（`swizzle 对应地址重映射、张量核心对应计算单元、TMA 对应数据搬运`）✅。
2. **本讲对外的承诺**：L26（四块内容耦合更紧，L180–190 兑现 ✅）、L190（第 20 讲内核超优化）、
   L198（后面几讲换硬件再走一遍 → 第 15 讲 TIRx 即此）。反向检索（`第 13 讲`）命中的都是**回指**，不是承诺。

---

## 我核不到的（诚实记录）

1. **主页面嵌入但未缓存的 3 个 `demo/` 页**：`swizzle_8x8`、`swizzle_128B`、`swizzle_atom_general`（见 P1-1）。
   ⇒ 因此这些**关于源的主张我核不到、不判对错**：
   - L34–L40「上一讲最后的例子是 8 乘 8 的方块……做法是对列号做一次异或，目的是让同一列的多行落在不同的 bank 上」
     （**机制本身**在 `swizzle_atom_128b.html` / `tiling_exploration.html` 里有逐字依据 ✅，但「上一讲那一页 8×8 演示」这一份 HTML 没拿到）；
   - L138「swizzle **有很多种格式**」中「全格式」那一页（`swizzle_atom_general`）的内容（四种格式 128B/64B/32B/16B 在 `why_128b.html` 的 `FORMATS` 数组里已核到 ✅）。
2. **仓库里另 7 个 `demo/` 文件未被主页面嵌入**（`swizzle_atom_64b`、`tensor_core_basics`、`tensor_core_swizzle`、
   `tiling_constraint`、`tma_basics`、`tma_swizzle`、`tma_tiling`，见 `mlsys-webrepo-tree.txt` L149/151/153/155/158/160/161）——
   它们不在嵌入清单里，所以不算本讲的证据面，我也没读。
3. **交互过程**：源页的动画/点击/播放（swizzle 逐周期演示、K 步进播放、hover 箭头）我**只读了源码**，没有真的点。
   正文没有依赖点击过程，但 L148「课件在图里把不同格式下每一行的连续长度**高亮**出来」这类描述只能从源码的
   `Highlight row` 控件与 `.cell.hl` 推断，**未目视验证**。
4. **没有第二份独立抽取可比**（源是 HTML，不是 PDF；不存在 faithful/embedded 交叉验证）。
5. 检索词记录（用于 P1-1 与 P2-2）：`iframe`、`Outer K|Inner K|N block`、`XOR`、`16×16|M×16|M (output rows)`、
   `64 fp16|128B|byte`、`omitted`、`cooperative`。范围 = `evidence/gemm/` 全 9 份 + 主页面 + `mlsys-webrepo-tree.txt`。

---

## 覆盖面（附录十二）

- **正文**：218 行**逐行读完**；14 张配图**全部文本层通读**（脚本抽每张 SVG 的可见 `<text>` 与 `<title>/<desc>`）。
  逐条命中：`-3`（8×8 扇区列 ✅）、`-4`（XOR 公式 ✅）、**`-5`（「分块要能被 swizzle 原子整除」⇒ 与正文同一处 → P2-1）**、
  `-6`（M/N 四档 + K 固定 16 ✅）、`-7`（M×16 与 8×16B ✅）、`-8`（16×128 fp16 ✅）、`-9`（16×256、512 字节 ✅）、
  `-10`（两侧理由 + 64 fp16 ✅）、`-11`（四步 ✅）、**`-12`（「两重循环」⇒ 与正文同一处 → P0-1）**、
  `-13`（三层约束 ✅）、`-1`/`-2`/`-14`（无数字，与正文一致 ✅）。
  ⇒ **P0-1 要改正文 L172 与图 12 的可见文字两处**，**P2-1 要改正文 L72 与图 5 的可见文字（+`desc`）两处**，
  **P2-2 里的 L150/L176/L100/L64 只需改正文（或补溯源）**，其各条**只需改正文**。
- **未验**：上面「我核不到的」1–5。

---

**核对人声明**：本记录只覆盖开头那个哈希的版本（`E283D1CD9A2280D1`）。对其它版本的结论不成立。
本记录只读正文、不修改任何 `content/` 文件；`status` 由 Lead 处理。
