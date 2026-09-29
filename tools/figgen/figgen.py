"""CourseLingo 配图几何生成器（仓库外工具）。

目的：把 svg-lint 房规里**可以做对的算术**从"每次手算"变成"构造出来就对"：

  · 框高 = 字号*3 + (行数-1)*字号*1.5          （box-height）
  · 框内基线由**块居中**公式反解，天然满足 baseline-offset
  · 同行相邻框间距固定 28px（25–30 区间内）      （block-spacing）
  · viewBox 四边留白**恒等于** MARGIN           （viewbox-clipping，且左右/上下必然对称）
  · 标题 x 用迭代法解到"内容 bbox 中心"           （title-not-centered）
  · 直线箭头端点按 5 / 11 补偿                    （arrow-marker）
  · 文字宽度用与 linter 同一张字宽表预估           （text-overflow）

不做的：版面设计。版面仍然每张单独想。
"""
from __future__ import annotations

import math
import pathlib

MARGIN = 23          # 四边留白，房规 20–25
GAP = 28             # 相邻框间距，房规 25–30
TITLE_FS = 16

PAL = {
    "input": ("#dbeafe", "#3b82f6", "#1e40af"),
    "proc": ("#fef3c7", "#f59e0b", "#b45309"),
    "out": ("#d1fae5", "#22c55e", "#166534"),
    "ana": ("#f3e8ff", "#a855f7", "#6b21a8"),
    "warn": ("#fce7f3", "#ec4899", "#9d174d"),
    "neut": ("#eff6ff", "#3b82f6", "#1e40af"),   # 已登记的品牌色 #eff6ff
}
PAL["analysis"] = PAL["ana"]                     # 别名，省得记缩写
PAL["processing"] = PAL["proc"]
PAL["output"] = PAL["out"]
PAL["warning"] = PAL["warn"]
T_MAIN = "#1e293b"
T_SUB = "#64748b"
T_WEAK = "#94a3b8"
ARROW = "#64748b"
GROUP_FILL = "#f8fafc"
GROUP_STROKE = "#94a3b8"

# linter 的字宽表（lib/text-metrics.mjs），照抄
_TABLE = {8: (4.5, 8), 9: (5.0, 9), 10: (5.5, 10), 11: (6.0, 11), 12: (7.0, 12)}


def _widths(fs: float) -> tuple[float, float]:
    if fs == int(fs) and int(fs) in _TABLE:
        return _TABLE[int(fs)]
    return (fs * 0.58, fs)


def _is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x2E80 <= cp <= 0x9FFF
        or 0xF900 <= cp <= 0xFAFF
        or 0xFE30 <= cp <= 0xFE4F
        or 0xFF00 <= cp <= 0xFF60
        or 0x20000 <= cp <= 0x3FFFF
    )


def text_w(s: str, fs: float) -> float:
    latin, cjk = _widths(fs)
    return sum(cjk if _is_cjk(c) else latin for c in s)


def jsround(v: float) -> int:
    """JS Math.round：.5 向上取整（Python 的 round 是银行家舍入，不能用）。"""
    return math.floor(v + 0.5)


class Fig:
    def __init__(self, vid: str, title: str, desc: str):
        self.vid = vid
        self.title = title
        self.desc = desc
        self.body: list[str] = []
        self.rects: list[tuple[float, float, float, float]] = []
        self.texts: list[tuple[float, float, str, float]] = []
        self.paths: list[list[tuple[float, float]]] = []

    # ---------- 图元 ----------

    def group(self, x, y, w, h, label=None, label_fs=11):
        """虚线分组框 + 左上角小节名（房规 §8.4）。"""
        self.rects.append((x, y, w, h))
        self.body.append(
            f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
            f'fill="{GROUP_FILL}" stroke="{GROUP_STROKE}" stroke-dasharray="6,4"/>'
        )
        if label:
            self.txt(x + 13, y + 14 + label_fs * 0.35, label, label_fs, T_SUB, "start")

    def box(self, x, y, w, lines, kind="input", h=None):
        """lines = [(text, font_size), ...]，第一行通常是标题行。

        h 显式给了就用它（跨行分组框要用），否则按房规公式算。
        """
        fill, stroke, tcol = PAL[kind]
        fs_max = max(fs for _, fs in lines)
        n = len(lines)
        need = fs_max * 3 + (n - 1) * fs_max * 1.5
        if h is None:
            h = math.ceil(need)
        assert h >= need - 0.5, f"[{self.vid}] 框高 {h} 不够：需要 {need}"
        # 相邻基线的间隔：取"后一行"的字号 * 1.5（字号相同的相邻两行必须正好是这个值）
        steps = [lines[i + 1][1] * 1.5 for i in range(n - 1)]
        block_fs = (lines[0][1] + lines[-1][1]) / 2
        total = sum(steps)
        mid = y + h / 2 + block_fs * 0.35
        base = mid - total / 2
        ys = []
        acc = base
        for i in range(n):
            if i:
                acc += steps[i - 1]
            ys.append(round(acc, 1))

        self.rects.append((x, y, w, h))
        self.body.append(
            f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'
        )
        cx = x + w / 2
        for (txt, fs), by in zip(lines, ys):
            tw = text_w(txt, fs)
            assert tw <= w - 4, f"[{self.vid}] 文字超出框：{txt!r} 需 {tw:.0f} > 可用 {w-4:.0f}"
            self.txt(cx, by, txt, fs, tcol)
        return h

    def txt(self, x, y, s, fs, fill, anchor="middle"):
        self.texts.append((x, y, s, fs, anchor))
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        self.body.append(
            f'  <text x="{x}" y="{y}" font-size="{fs}" fill="{fill}"{a}>{s}</text>'
        )

    def arrow_h(self, x_from, x_to, y, leftward=False):
        """x_from / x_to 是**框的边缘**；函数自己做 5 / 11 补偿。"""
        if not leftward:
            p1, p2 = x_from + 5, x_to - 11
            assert p2 - p1 >= 6, f"[{self.vid}] 右向箭头可见段太短：{p2-p1:.0f}"
            self._line([(p1, y), (p2, y)])
        else:
            p1, p2 = x_from - 5, x_to + 11
            assert p1 - p2 >= 6, f"[{self.vid}] 左向箭头可见段太短：{p1-p2:.0f}"
            self._line([(p1, y), (p2, y)])

    def arrow_v(self, y_from, y_to, x, upward=False):
        if not upward:
            p1, p2 = y_from + 5, y_to - 11
            assert p2 - p1 >= 6, f"[{self.vid}] 下向箭头可见段太短：{p2-p1:.0f}"
            self._line([(x, p1), (x, p2)])
        else:
            p1, p2 = y_from - 5, y_to + 11
            assert p1 - p2 >= 6, f"[{self.vid}] 上向箭头可见段太短：{p1-p2:.0f}"
            self._line([(x, p1), (x, p2)])

    def _line(self, pts):
        self.paths.append(pts)
        d = "M" + " L".join(f"{px},{py}" for px, py in pts)
        self.body.append(
            f'  <path d="{d}" fill="none" stroke="{ARROW}" stroke-width="1.5" '
            f'marker-end="url(#arrow)"/>'
        )

    # ---------- 栈布局（y / x 由上一块的实测高度推出，杜绝手算错位）----------

    def vstack(self, x, y, w, specs, gap=25):
        """specs = [(lines, kind), ...]；返回 [(y, h), ...]。"""
        out = []
        for lines, kind in specs:
            h = self.box(x, y, w, lines, kind)
            out.append((y, h))
            y += h + gap
        return out

    def hstack(self, x, y, w, specs, gap=28):
        """specs = [(lines, kind), ...]；返回 [(x, h), ...]。"""
        out = []
        for lines, kind in specs:
            h = self.box(x, y, w, lines, kind)
            out.append((x, h))
            x += w + gap
        return out

    # ---------- 输出 ----------

    def render(self) -> str:
        # 内容 bbox（不含标题）
        xs = [r[0] for r in self.rects] + [r[0] + r[2] for r in self.rects]
        ys_ = [r[1] for r in self.rects] + [r[1] + r[3] for r in self.rects]
        for x, y, s, fs, anchor in self.texts:
            w = text_w(s, fs)
            if anchor == "start":
                xs += [x, x + w]
            elif anchor == "end":
                xs += [x - w, x]
            else:
                xs += [x - w / 2, x + w / 2]
            ys_ += [y - fs * 0.75, y + fs * 0.25]
        for pts in self.paths:
            xs += [p[0] for p in pts]
            ys_ += [p[1] for p in pts]
        cmin_x, cmax_x, cmin_y, cmax_y = min(xs), max(xs), min(ys_), max(ys_)

        # 标题：迭代解到最终内容 bbox 的中心（标题自身也在 bbox 内 → 求不动点）
        tw = text_w(self.title, TITLE_FS)
        title_y = cmin_y - 22
        cx = (cmin_x + cmax_x) / 2
        for _ in range(8):
            mnx = min(cmin_x, cx - tw / 2)
            mxx = max(cmax_x, cx + tw / 2)
            ncx = (mnx + mxx) / 2
            if abs(ncx - cx) < 1e-9:
                break
            cx = ncx
        mnx = min(cmin_x, cx - tw / 2)
        mxx = max(cmax_x, cx + tw / 2)
        mny = min(cmin_y, title_y - TITLE_FS * 0.75)
        mxy = cmax_y

        vx, vy = mnx - MARGIN, mny - MARGIN
        vw = (mxx - mnx) + 2 * MARGIN
        vh = (mxy - mny) + 2 * MARGIN
        vx, vy, vw, vh = round(vx, 1), round(vy, 1), round(vw, 1), round(vh, 1)

        head = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" '
            f'width="{vw}" height="{vh}"',
            f'     role="img" aria-labelledby="fig-{self.vid}-title fig-{self.vid}-desc">',
            f'  <title id="fig-{self.vid}-title">{self.title}</title>',
            f'  <desc id="fig-{self.vid}-desc">{self.desc}</desc>',
            "",
            "  <defs>",
            "    <style>",
            "      text { font-family: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-serif; }",
            "    </style>",
            '    <marker id="arrow" markerWidth="8" markerHeight="8" refX="2" refY="4"',
            '            orient="auto" markerUnits="userSpaceOnUse">',
            f'      <path d="M0,0 L8,4 L0,8 L2,4 z" fill="{ARROW}"/>',
            "    </marker>",
            "  </defs>",
            "",
            f'  <rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="#ffffff"/>',
            "",
            f'  <text x="{round(cx,1)}" y="{round(title_y,1)}" font-size="{TITLE_FS}" '
            f'font-weight="600" fill="#1f2937" text-anchor="middle">{self.title}</text>',
        ]
        return "\n".join(head + self.body) + "\n</svg>\n"

    def fingerprint(self) -> str:
        """与 audit_content.py 的 layout_fingerprint 同一算法。"""
        boxes = []
        for (x, y, w, h) in self.rects:
            boxes.append((jsround(x / 10), jsround(y / 10), jsround(w / 10), jsround(h / 10)))
        return ";".join(f"{a},{b},{c},{d}" for a, b, c, d in sorted(boxes))

    def save(self, path: pathlib.Path):
        path.write_text(self.render(), encoding="utf-8")
