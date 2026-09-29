# figgen —— 把配图房规的算术**构造性**做对

> 这是 CourseLingo 课程仓的**配图几何生成器**。它不负责版面设计，只负责让
> 「算出来的坐标」一次就过 `tools/svg-lint`。
>
> 规范本身见 [`docs/figure-spec.md`](../../docs/figure-spec.md)。本文件只讲**怎么用**与**它保证什么**。

## 为什么要有它

房规里有一批**纯算术**要求，手算每次都可能错，而错了以后 linter 只会告诉你结果错：

| 房规项 | 手算容易错在哪 |
| --- | --- |
| 框高 = 字号 × 3 + (行数−1) × 字号 × 1.5 | 单行 13px 想当然写成 42，实际是 39，于是下面所有 y 全错位 |
| 框内基线用**块居中**公式 | 多行框按「第一行 y+28」硬套，遇到 3 行、4 行就偏 |
| 相邻框 25–30px | 跨行分组框的高度没跟着内容长，下一块就变成 39px、66px 的缝 |
| viewBox 四边 20–25px 且左右/上下对称 | 只调了一边 |
| 标题对齐**内容**中心 | 内容不对称时标题就偏了 |
| 箭头 5 / 11 补偿 | 换成 12×12 的箭头时补偿量是 14 / 17，不是 11 |

**这些都能用「构造」解决，不该用「画完再量」解决。** 本项目在这一类错上反复踩过，
所以把算术收进一个地方，只在这里改。

## 它保证什么

用 `Fig` 的方法画图，下列各项**由构造保证成立**（已对本课程 40 张图实测 0 error / 0 warning）：

- **框高**：默认按 `ceil(fs_max × 3 + (行数−1) × fs_max × 1.5)` 算；显式传 `h=` 时**断言**不小于房规下限
- **框内基线**：由「块居中」公式反解，多行框的第一行与最后一行基线中点必然落在
  `y + h/2 + ((fs_first+fs_last)/2) × 0.35`，相邻同字号行间距恒为 `fs × 1.5`
- **框内文字**：`text-anchor="middle"` 且 x 恒等于框中心；写入前用**与 linter 同一张字宽表**断言不溢出
- **viewBox**：四边留白**恒等于** `MARGIN`（默认 23），因此左右、上下必然对称
- **标题**：用不动点迭代解到最终内容 bbox 的中心（标题自身也在 bbox 内，所以必须迭代）
- **箭头**：`arrow_h` / `arrow_v` 收的是**框的边缘坐标**，自己做 5 / 11 补偿，并断言可见段 ≥6px
- **栈布局**：`vstack` / `hstack` 用上一块的**实测高度**推出下一块的位置，杜绝手算错位
- **marker**：按房规写好 `markerUnits="userSpaceOnUse"`、`orient="auto"`、`refX/refY`、8×8

## 它不保证什么（仍然要自己看）

这几条房规 linter 查不到，生成器也不管，交付前**必须自己看**：

1. **版面要与内容匹配**（`figure-spec.md` §7）。生成器只保证几何合法，不保证你选对了版面。
   流程图别画成网格，对比别画成链。
2. **版面指纹不要重复**。`audit_content.py` 会按「图内方块的 (x,y,w,h) 舍入到 10px 后排序」
   判重，超过 15% 警告、25% 报错。`Fig.fingerprint()` 用的是**同一套算法**，
   所以可以在生成脚本里自查（见下）。
3. **标题/分组框名的用词**、连线是否有意义（§8.5）、左右配重（§8.2）。

## 用法

```python
from figgen import Fig

f = Fig("my-figure-1", "图的标题", "一句话说清图里有什么、结论是什么")

# 单行框：高度自动
f.box(25, 70, 340, [("ML 模型", 14)], "input")

# 多行框：第一行通常是标题行
f.box(25, 137, 340, [("自动微分", 15), ("反向图自动搭出来", 12)], "proc")

# 跨行分组框：显式给高度（内容必须放得下，否则断言失败）
f.box(393, 70, 300, [("模型侧", 15), ("写代码的人在这一层", 12)], "input", h=176)

# 虚线分组框 + 左上角小节名
f.group(25, 56, 712, 163, "一台训练节点", )

# 栈布局：y 由上一块的实测高度推出，返回 [(y, h), ...]
ys = f.vstack(25, 70, 340, [([("第一层", 14)], "input"), ([("第二层", 14)], "proc")])

# 箭头：给的是**框的边缘**，补偿由函数做
f.arrow_h(240, 268, 114)                 # 右向：源右缘 → 目标左缘
f.arrow_h(496, 468, 114, leftward=True)  # 左向
f.arrow_v(148, 176, 368)                 # 下向
f.arrow_v(166, 138, 278, upward=True)    # 上向

f.txt(381, 356, "（来源：课件时间轴）", 10, "#94a3b8")   # 自由文字，anchor 可给 start / end

f.save(OUT / "my-figure-1.svg")
```

调色板只提供房规允许的语义色：`input / proc / out / ana / warn / neut`
（另有 `processing / output / analysis / warning` 三个别名）。

## 生成脚本的自查模板

每讲一个 `build_lNN.py`：逐张 `save()`，同时把**版面指纹**收进一个字典，
最后打印有没有重复。这与 `audit_content.py` 的判据一致，因此能**在跑 lint 之前**发现撞版。

```python
seen: dict[str, list[str]] = {}
for f in figs:
    f.save(OUT / f"{f.vid}.svg")
    seen.setdefault(f.fingerprint(), []).append(f.vid)
dup = {k: v for k, v in seen.items() if len(v) > 1}
print("版面指纹重复：" if dup else "指纹互不相同", list(dup.values()))
```

## 交付前仍然要跑的闸门

```powershell
python scripts/check_figures.py --root . --strict   # 房规 0 error / 0 warning
python scripts/audit_content.py --root . --strict   # 密度、小节配图、版面复用、图文上下文
```
