# 质量审核记录 · 01-why-ml-systems（第 1 讲）

> §9 要求：`status = "reviewed"` 的前置条件是「**P0/P1 清零 + 有审核记录**」。
> 本文件就是那份记录。审核人：CourseLingo Lead（非本讲作者 `mlsys-author`）。

## 1. 被审核版本

| 项 | 值 |
| --- | --- |
| 页面 | `content/01-why-ml-systems/index.md` |
| 归一化哈希（CRLF→LF 后 SHA256 前 16） | `6CBE59318BBAF47B` |
| 讲次 | 第 1 讲 · Why ML Systems? |
| 源材料 | <https://mlsyscourse.org/slides/01-course-introduction.pdf> |
| 产出形态 | `output_mode = "explanation"`（依 `courselingo/docs/output-mode-decision.md` §3） |

## 2. 五道机检（Lead 自己跑，不采信作者的 exit code）

| 闸门 | 退出码 |
| --- | --- |
| `validate.py --root .` | 0 |
| `check_style.py --root .` | 0 |
| `audit_content.py --root . --strict` | 0（0 ERROR / 0 WARN） |
| `check_figures.py --root . --strict` | 0（11 张图，0 error / 0 warning） |
| `build_site.py --root . --out site-mkdocs` | 0 |

## 3. 第一道人工闸门 · 非作者事实核对

- 记录：`docs/audit/why-ml-systems-factcheck.md`
- 核对人：`mit65840-reviewer`（**非本讲作者**）
- **核对结论：P0 0 ｜ P1 1 ｜ P2 1**
- **P1 的内容**：五处术语/机制展开在 faithful 文本层里找不到依据，且**未纳入页面已写好的**
  「课件没有展开的推论属于 CourseLingo 的讲解」这句声明。
- **处置**：作者已修（commit `1b3aced`）—— 在相应位置就近标注为我们自己的归纳。
- **P2 的内容**：L54「2017 年**之后**」而课件只写 `2017`。**处置**：已改。

**★ 核对者写清了它核不到的东西**（课件那页文字顺序无法唯一确定 2016↔张量核心 / 2017↔公有云的版面绑定），
**并声明了检索范围** ⇒ 符合本项目「否定性结论要最高标准」的要求。

## 4. 第二道人工闸门 · 配图视觉复核

- 报告：`docs/audit/visual-review/mlsys-15442__why-ml-systems-*.md`（11 张）
- 复核模型：`qwen3.8-max`
- **结论：11 张中 9 张可用、1 张需小修、1 张有错误**
- **处置**：
  - 「有错误」那张：`why-ml-systems-3`（时间轴分期重叠 2006–2010）⇒ **已改**
  - 「需小修」那张：`why-ml-systems-1`（用 `×` 连接百分数与毫秒，量纲不通）⇒ **已改**
- **本记录写入时，11 张报告均已针对当前 SVG 版本**（按报告内的 `复核对象 SHA256` 比对）。

## 5. 本轮修复引入了什么新错

**本轮没有新引入的错误。** 但有两处**我自己造成的返工**值得记：

1. **正文一处越界**（作者自己报的）：原写「两块 GTX 580 单卡显存装不下当时的网络」，
   而**课件只写了卡型号、没写显存** ⇒ 该句已显式标注为背景补充。**这是「不把推断说成原文」的标准动作。**
2. **`text-clean/*.txt` 一度被当成「PDF 文本层」的证据**（作者连改三次）：
   根因是 `_sources/_audit/clean_text.py` 的 `despace()` 正则
   `re.sub(r"(?<=\b\w) (?=\w\b)", "", s)` **只合并「左右各恰好一个字母」的空格**，
   于是 `Mac hi ne` 这类 kern 分段一个都没合并掉。
   **⇒ 判据只能是 `pdftext3.py` 的输出（`.faithful.txt`）；9 份缓存 PDF 全部可用。**
   **⇒ 立为 `courselingo/docs/quality-audit.md` 附录十九「改了结论 ≠ 重新取了证」。**

## 6. 本轮删掉了什么

**没有删除任何内容。**（本讲是本课程的第一次提级，此前一直在补内容。）

## 7. 结论

**⇒ P0 = 0，P1 已清零，两道人工闸门均已过，五道机检全绿。**
**⇒ 同意提为 `status = "reviewed"`。**

**⚠️ 授权侧的诚实边界（不变）**：本讲是 `explanation`（原创讲解）。
若日后要改为 `transcript`，**须先对本讲实际依据的那份课件单独取证一次**
（逐页原则，见 `courselingo/docs/output-mode-decision.md` §6）。
