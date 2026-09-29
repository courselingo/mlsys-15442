# 配图作业规范 · Figure Spec（可机检）

> 这是**作业规范**，不是设计随想。设计理由见 [diagram-conventions.md](./diagram-conventions.md)。
>
> **先看 [figure-audit.md](./figure-audit.md) 决定「这里该不该有图」，**
> 再回来看本文件决定「怎么画」。顺序反了就会出现「图都合规，但该画的地方空着」。
> 每条规则都由房规 linter 实际校验过，**照做就能 0 error 0 warning**。

## 0. 一句话

手绘 SVG、单一浅色底、中文标签居中、只用房规调色板、线走曲线不走直角。
**不要用 Mermaid，不要用 CSS class 上色。**

## 1. 交付前必须跑的命令

**PowerShell 不会替原生命令展开通配符** —— 直接写 `...\figures\*.svg` 会让 CLI
拿到字面量 `*.svg` 并以 ENOENT 退出（退出码 2）。必须显式展开：

```powershell
# ✅ 推荐：交给封装脚本，它自己枚举文件
python scripts/check_figures.py --root . --strict

# ✅ 手动跑 linter：用 Get-ChildItem 展开
$node = "C:\Users\keriko\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
& $node tools\svg-lint\bin\svg-lint.mjs (Get-ChildItem content\<页面目录>\figures\*.svg).FullName

# ❌ 错：字面量通配符，退出码 2
& $node tools\svg-lint\bin\svg-lint.mjs content\<页面目录>\figures\*.svg
```

- 退出码 `1` = 有 error。**必须修到 `0 error(s), 0 warning(s)`。**
- 只想看 error：加 `--quiet`。
- node 不在 PATH 时用 `COURSELINGO_NODE` 指过去。
- 肉眼复核可以把单张 SVG 交给浏览器光栅化（Windows 上 `msedge.exe` / `chrome.exe`
  加 `--headless=new --screenshot=out.png --window-size=W,H`），再量一次真实墨迹边距。

## 2. 调色板（**只能用这些**）

写别的十六进制色值 → `palette-conformance` 直接报 warning。

| 用途 | fill | stroke | text |
| --- | --- | --- | --- |
| input | `#dbeafe` | `#3b82f6` | `#1e40af` |
| processing | `#fef3c7` | `#f59e0b` | `#b45309` |
| output | `#d1fae5` | `#22c55e` | `#166534` |
| analysis | `#f3e8ff` | `#a855f7` | `#6b21a8` |
| warning | `#fce7f3` | `#ec4899` | `#9d174d` |

文本色：`#1e293b`（主）/ `#64748b`（次）/ `#94a3b8`（弱）。
箭头：`#64748b`、`#3b82f6`、`#f59e0b`、`#22c55e`、`#a855f7`、`#ef4444`。
分组框：fill `#f8fafc`、stroke `#94a3b8`、`stroke-dasharray="6,4"`。
画布：`#ffffff`。

**CourseLingo 已额外登记的 4 个品牌色**（本项目补丁）：`#2563eb`、`#1f2937`、`#1d4ed8`、`#eff6ff`。
除这 4 个之外，仍只能用上表。

## 3. 骨架（照抄，改内容即可）

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 260" width="760" height="260"
     role="img" aria-labelledby="fig-x-title fig-x-desc">
  <title id="fig-x-title">图的中文标题</title>
  <desc id="fig-x-desc">一句话说清图里有什么、结论是什么。</desc>

  <defs>
    <style>
      text { font-family: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-serif; }
    </style>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="2" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 L2,4 z" fill="#64748b"/>
    </marker>
  </defs>

  <rect x="0" y="0" width="760" height="260" fill="#ffffff"/>

  <text x="380" y="34" font-size="16" font-weight="600" fill="#1f2937" text-anchor="middle">图的中文标题</text>
  <!-- 方块与连线 -->
</svg>
```

### 硬性细节（漏一条就报错）

1. **必须有 `<style>` 且里面有一条 `text { font-family: ... }` 规则**，字体栈照抄上面。
   —— 只写 class 选择器（如 `.lbl`）不算，会报 `missing-font-stack`。
2. **marker 必须同时写 `markerUnits="userSpaceOnUse"` 和 `orient="auto"`**，`markerWidth` 只能是 **8 / 12 / 16**。
3. **第一个绘制元素是画布矩形** `fill="#ffffff"`，覆盖整个 viewBox。
4. **`<title>` / `<desc>` 是根元素前两个子元素**，`aria-labelledby` 把两者都接上。
5. **方块内的文字必须 `text-anchor="middle"`**（水平居中于方块中心）。
   —— 左对齐/右对齐的方块标签会报 `label-not-centered`。
6. **上色一律用呈现属性**（`fill=` / `stroke=` 写在元素上），**不要用 CSS class 上色**。
7. **不要写直角折线，也不要写斜的直线段** —— 转角用 `C`/`Q` 曲线；直线只在两端同轴时用。

## 4. 几何规则（数值是硬性的）

| 项 | 要求 |
| --- | --- |
| viewBox 边距 | **20–25px**，左右相差 ≤5px |
| 方块之间的间距 | **25–30px**（低于 25 箭头会退化成点） |
| 方块高度 | `font-size × 3 + (行数 − 1) × (font-size × 1.5)` |
| 行距 | `font-size × 1.5`（12px 字 → 18px；15px 字 → 22.5px） |
| 同一行内方块宽度 | 相差 **≤60px** |
| 箭头起点/箭尖留白 | 距源/目标方块各 **5px** |
| 绕行路径 | 距无关方块 ≥20px |

### 两行方块的算例（最常用）

方块 `y=68, h=68`，第一行 15px、第二行 12px：

```
基线1 = y + 28 = 96      （15px 字）
基线2 = y + 50 = 118     （12px 字）
```

## 5. 页面里怎么引用

```markdown
![一句话说清「图里有什么 + 结论是什么」的中文 alt](figures/xxx.svg)
```

- 图放在**本页目录**的 `figures/` 下，与 `index.md` 同级。
- 文件名：`<slug>-<n>.svg`，`n` 从 1 开始。
- **alt 不是「示意图」** —— 要能替代图片传达信息，≤60 字。
- 图前面写一句引出、图后面写一句解读，不要让图孤零零挂着。

## 6. 常见报错对照

| 报错 | 改法 |
| --- | --- |
| `missing-font-stack` | `<style>` 里加 `text { font-family: ... }` |
| `marker-units-missing` / `marker-orient-missing` | marker 补 `markerUnits="userSpaceOnUse"` / `orient="auto"` |
| `label-not-centered` | 方块内文字加 `text-anchor="middle"` |
| `box-too-short` | 方块高度按 §4 公式算 |
| `row-box-size-mismatch` | 同行方块宽度差压到 ≤60px |
| `margin-too-large` / `horizontal-margin-asymmetric` | 收紧 viewBox，左右留白对齐 |
| `diagonal-straight-line` | 斜线改成 `C`/`Q` 曲线 |
| `off-palette-color` | 换成 §2 里的色值 |
| `spacing-too-small` | 方块间距加到 ≥25px |
| `arrow-start-clearance` / `arrow-tip-clearance` | 线端离方块 5px |


### 6.1 ★ 双向连接怎么画（**不要用 `marker-start`**）

**房规里没有「双向箭头」这个图元。** 做法是 **画两条反向的 path，各自只带 `marker-end`**：

```xml
<!-- 竖直边（上→下）-->
<path d="M203,161 L203,171" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>
<!-- 竖直边（下→上）-->
<path d="M203,177 L203,167" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>
```

**为什么不加 `marker-start`**：`orient="auto"` 让 marker 沿**路径前进方向**，
所以 `marker-start` 画的头**也朝前** ⇒ **两个头同向叠置**，看起来是双向、实际不是。
（本仓的 lint 强制 `orient="auto"`，而它的注释里已写明这个取舍与 1px 侵入。）

**直线上的补偿量是 11，不是 5**：

```
marker 规格 { size: 8, refX: 2, tip: 6, endOffset: 11 }
                                      ↑ 箭头伸出   ↑ 11 = 5(留白) + 6(伸出)
⇒ 向下: 起点 = 上框底 + 5      终点 = 下框顶 − 11
   向上: 起点 = 下框顶 − 5      终点 = 上框底 + 11
```

**★ 曲线上不能照搬 11 —— 这是切向问题，不是端点问题**：

**直线的 11px 补偿建立在「尖端沿线段方向伸出」上**；而**弧的端点是斜着到达框的，尖端沿切向伸出**。
⇒ **同样的端点坐标，起点距框与尖端落点都不是 11 − 6 那套算术。**

**实测（`intro-2`，两框左缘 x=60，`tip=6`）**：
```
反向弧 M55,310 C 30,265 29,161 52,122
  起点 (55,310) 切向 (−0.486,−0.874) 尖端 (52.09,304.76) ⇒ 距框 7.91px  ✗（房规要 5）
正向弧 M52,122 C 29,161 30,265 55,310
  终点 (55,310) 切向 ( 0.486, 0.874) 尖端 (57.91,315.24) ⇒ 距框 2.09px  ✗
```

**⇒ 正确做法：按切向解端点，而不是把一条弧的 `d` 反过来。**
（`tip` 落在 `端点 + tip × 切向单位向量`，令它与框的距离 = 5 解出端点。）

**解出的可行值（已过 lint 0/0）**：
```xml
<path d="M55,122 C 32,161 33,265 52.6,310" ... marker-end="url(#arrow)"/>
<path d="M55,310 C 30,265 29,161 52.0,122" ... marker-end="url(#arrow)"/>
```
**★ 注意两个终点是 52.6 与 52.0，不是彼此的反演** —— **弧上两条反向 path 要各自解自己的端点。**


## 7. ★ 版面必须与内容匹配（不要什么都画成网格）

**实测教训**：第一轮批量补图后，**145 张里有 62 张（43%）用了完全相同的版面** ——
同样是六个 220×50 的方块摆成 3×2 网格，只有文字不同。几何全过、房规全过、密度也达标，
但读者连着看到同一个形状几十次，**视觉通道就失效了**：
图变成了「把文字装进框里」，而不是在讲关系。

问题不在于「网格不好」，而在于**网格被用来装一切**。
下面这些内容塞进网格就是错的：

| 内容在讲 | 网格为什么错 | 该用的版面 |
| --- | --- | --- |
| **脑裂：断成两半** | 网格看不出「两半」 | 左右两组 + 中间断开的链路 |
| **阶段一的两条分支** | 网格没有分叉 | 一进二出的分叉（`C`/`Q` 曲线） |
| **日志匹配 / 前缀检查** | 网格看不出「对齐」 | 两条平行日志条，逐格对齐 |
| **任期作为逻辑时钟** | 网格没有时间 | 横向时间轴 + 刻度 |
| **三个时间尺度** | 同上 | 三条并列的时间轴（长度可比） |
| **只监视前一个（链）** | 网格没有顺序 | 横向链式箭头 |
| **版本号 / 编号递增** | 网格没有递增感 | 时间轴或递增刻度 |
| **延迟下界** | 网格看不出长度 | 水平条形 + 刻度 |
| **角色转换** | 网格没有环 | 环形箭头（双向） |
| **层次 / 包含关系** | 网格没有层级 | 树或嵌套框 |
| **吞吐 vs 延迟（取舍）** | 网格没有对立 | 左右双列 + 中间的取舍箭头 |

### 版面词汇表（先选版面，再填内容）

| 版面 | 用在 | 视觉特征 |
| --- | --- | --- |
| **链** | 流程、时序、管道 | 一排方块 + 同轴箭头 |
| **分叉** | 条件分支 | 一进多出，`Q` 曲线 |
| **环** | 状态机、角色转换 | 方块围成圈 + 弧线箭头 |
| **时间轴** | 任期、编号、延迟 | 一条横线 + 刻度 + 上方事件 |
| **双列对照** | 取舍、对比、正反例 | 两列 + 中间分隔或对比标记 |
| **分组（泳道）** | 归属、分区、断成两半 | 虚线框包住若干方块 |
| **树 / 嵌套** | 层次、包含、分工 | 上下层或框套框 |
| **平行对齐** | 日志、副本、逐步比对 | 两条以上等宽横条逐格对齐 |
| **网格** | **真正的清单 / 参数表**（只在此时用） | 等大方块阵列 |

### 怎么自查

```bash
# 语料级：同一版面指纹是否被过多图复用（>15% 警告，>25% 报错）
python scripts/audit_content.py --root .
```

`audit_content.py` 会输出类似：
```
[版面复用] 62/145 张图（43%）的版面完全一致……只有文字不同。
```

**看到这个警告，不要去改指纹，要去改版面** —— 逐张问：
「这张图讲的是关系还是清单？」关系就用上面对应的版面，只有真清单才用网格。


## 8. 房规查得到 vs 查不到

`tools/svg-lint/` 已经覆盖了下列**全部机检项**（12 条规则）：

| 规则 | 查什么 |
| --- | --- |
| `text-overflow` | 文字超出框（按字号表估算 CJK 字宽） |
| `xml-escaping` | `&` `<` `>` 未转义（会让整张图渲染失败） |
| `box-height` | 框高是否 ≥ 字号 × 3 |
| `block-spacing` | 相邻框间距 ≥25px（推荐 25–30） |
| `baseline-offset` | 文字垂直居中（基线 = 框中心 + 字号×0.35） |
| `palette-conformance` | 是否用了房规调色板 |
| `font-stack` | 是否声明了 CJK 字体栈 |
| `connector-geometry` | 转弯是否用 C/Q 曲线（禁止直角肘） |
| `arrow-marker` | `markerUnits="userSpaceOnUse"`、两端留隙 |
| `overlap` | 文字/线/框互相压 |
| `viewbox-clipping` | 内容是否被 viewBox 裁掉 |
| `light-bg-fallback` | 浅色底兜底 |

**以下几条机检查不到，交付前必须自己看：**

### 8.1 标题要对齐**内容**的中心，不是 viewBox 的中心

```
内容中心 = (最左元素左边缘 + 最右元素右边缘) / 2
```

两者只在内容左右对称时才相等。内容偏左时标题跟着偏，整张图看起来「没摆正」。
内容整体偏心时不必改每个坐标，包一层 `<g transform="translate(dx,0)">` 平移即可，
`dx = (右边距 − 左边距) / 2` —— 但**记得同步改标题的 x**。

### 8.2 画完再退一步看整体

- **左右配重**：两半的视觉重量应当接近，差太多就加/减一个注释框
- **一行的框尺寸**：同一行相邻框的宽度差 **≤60px**（差太多像拼贴）
- **同列的框对齐同一条中心线**
- **别留大片空白**：内容明显小于 viewBox 就收紧间距或缩小 viewBox
  （常见原因：框间距 >30px、边距 >25px、分组框内边距过大）

### 8.3 叠放次序（SVG 没有 z-index，后画的压在上面）

```
1. 最底层：分组框 / 泳道（虚线框，垫在所有东西下面）
2. 中间层：普通连接线与箭头
3. 上层：  方块与文字
4. 最上层：跨层的回环线（迭代回路、跨区域虚线）—— 必须最后画，否则被框盖住
```

**最常见的错**：先画连线再画分组虚线框 → 连线全被盖掉。

### 8.4 分组框的样式要统一

同一张图里的分组虚线框必须共用同一套属性：`stroke-dasharray`（建议 `6,4`）、
`rx`（8–12）、`fill`（`#f8fafc` 或 `none`）、内边距（15–20px）、标题字号（11px，
比正文 12px 小一档以示区分）。标题放在框内左上角：`x = 框 x + 10, y = 框 y + 14`。

**垂直居中的坑**：算分组框高度时要按**标题 + 内容**的总高算，不是只算内容 ——
有标题时顶部要被占掉约 20–25px，内部方块从标题下方开始。

### 8.5 连线必须有意义

每根箭头都要么有标签，要么**从上下文就能看出**它连的是谁、为什么。
看不出意图的连线应当删掉，而不是留着「显得完整」。

### 8.6 粗线要换大箭头

`stroke-width > 1.5` 时 8×8 的箭头显得太小：

| 线宽 | 箭头 | `refX` | 尖端外伸 | 终点公式 |
| --- | --- | --- | --- | --- |
| ≤1.5 | 8×8 | 2 | 6px | 目标边缘 − 11 |
| 1.5–2.5 | 12×12 | 3 | 9px | 目标边缘 − 14 |
| >2.5 | 16×16 | 4 | 12px | 目标边缘 − 17 |

### 8.7 ★ 图必须与正文同步改

> **一张与旁边正文矛盾的图，比没有图更糟。**

改动了正文里的数字、顺序或结论时，**同一个提交里**就要改对应的图。
这也是 `audit_content.py` 会检查「图前有引出句、图后有解读句」的原因：
图文互相绑定，改了一边就会立刻暴露另一边没跟上。
