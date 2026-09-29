"""核实配图版式是否真的重复（按「单节内最大同版式组 / 该节图数」，阈值 1/3）。

起因：事实核对者指出 GFS 一节 16 张里「12 张只有文字不同（上 3 框 / 下 3 框、
209×68、x=38/275/512）」，而 fig-pruner 此前报「最大组 8/85 = 9%」。

**两个数字都是真的，而且不矛盾** —— 全局比例掩盖了一节内部的重复。
读者体验的不是全局比例，是**连着翻到五张同构图**的感受。

做法：取每张 SVG 的全部 `<rect>`（排除画布本身），把 x/y/w/h 归一化成 viewBox 比例后
排序拼接成指纹，同指纹即几何完全同构。**归一化是必需的** —— 否则画布尺寸不同的图
会被当成不同版式。

判据：`单节最大同版式组 / 该节图数 > 1/3` 即需重排。
★ 不要用固定张数当阈值（曾写 `mx >= 4`）：那会把大节与小节放在同一把尺子上 ——
16 张里的 4 张是 25%（合规），9 张里的 4 张是 44%（超标）。

用法：
    python layout_check.py [课程根目录]      默认 mit-6.5840
"""
from __future__ import annotations

import pathlib
import re
import sys
from collections import Counter, defaultdict

DEFAULT_COURSE = r"D:\Vibe_Workspace\courselingo\courses\mit-6.5840"
_arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COURSE
ROOT = pathlib.Path(_arg).resolve()
# 允许传「课程根目录」或「content 目录」
if (ROOT / "content").is_dir():
    ROOT = ROOT / "content"
print(f"课程：{ROOT.parent.name}")



def fingerprint(svg: pathlib.Path) -> str | None:
    t = svg.read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([\d.\s-]+)"', t)
    if not vb:
        return None
    p = [float(x) for x in vb.group(1).split()]
    W, H = p[2], p[3]
    boxes = []
    for m in re.finditer(r"<rect\b([^>]*?)/?>", t):
        a = m.group(1)
        g = lambda k: (re.search(rf'{k}="([\d.]+)"', a) or [None, None])[1]
        x, y, w, h = g("x"), g("y"), g("width"), g("height")
        if None in (x, y, w, h):
            continue
        x, y, w, h = float(x), float(y), float(w), float(h)
        # 排除画布本身
        if w >= W - 1 and h >= H - 1:
            continue
        boxes.append((round(x / W, 2), round(y / H, 2), round(w / W, 2), round(h / H, 2)))
    if not boxes:
        return None
    return "|".join(f"{a},{b},{c},{d}" for a, b, c, d in sorted(boxes))


print()
print("=== 按「单节内最大同版式组 / 该节图数」判定（阈值 1/3）===")
worst = 0.0
for sec in sorted(p.name for p in ROOT.iterdir() if p.is_dir() and (p / "figures").is_dir()):
    g: dict[str, list[str]] = defaultdict(list)
    for svg in sorted((ROOT / sec / "figures").glob("*.svg")):
        f = fingerprint(svg)
        if f:
            g[f].append(svg.stem)
    n = len(list((ROOT / sec / "figures").glob("*.svg")))
    if not n:
        continue
    mx = max((len(v) for v in g.values()), default=0)
    ratio = mx / n
    worst = max(worst, ratio)
    # ★ 判据是**比例**，不是固定张数。
    #   曾经写 `mx >= 4` 判「重复严重」，那是把大节与小节放在同一把尺子上：
    #   16 张里的 4 张 = 25%（合规），而 9 张里的 4 张 = 44%（超标）。
    flag = "  <-- 超 1/3，需重排" if ratio > 1 / 3 else "  OK"
    print(f"  {sec:<34} {n:>2} 张 -> 最大组 {mx}  ({ratio:.0%}){flag}")
print(f"\n  本课程最高重复比例 {worst:.0%}  —— " +
      ("有章节超 1/3" if worst > 1 / 3 else "全部合规"))

