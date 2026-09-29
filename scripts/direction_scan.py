#!/usr/bin/env python3
"""方向词扫描 —— 把页面里所有「方向性/归属性」的句子列出来，供核对者逐句回源。

## 为什么需要这个

本项目四次独立事实核对里，反复出现的**不是「事实记错」，而是「方向反了 / 归属错了」**：

  GFS        `B/T + R×L` 被标成「**不做**流水线时」的耗时（实为流水线**之后**）
  Raft       「Raft **放弃了**写延迟的下界」（论文说它**达到了**下界）
  Raft       陈旧读归因到「**从跟随者读**」（实为一个已下台却未察觉的旧领导者）
  MapReduce  「它**放弃了中心化**的自由度」（应为**去中心化**）
  MapReduce  combiner 对最热单键「**无能为力**」（论文恰以最热键作 combiner 正面用例）
  6.006      「**第 2 讲**处理排序」（实为第 3 讲 —— 把模块号当成讲次号）
  CS168      「**幻灯片**说去掉 hello 只需更快」（出自教材）

**共同点**：命题本身往往在别处**都有据**，所以「事实对不对」这一问会全部通过；
错的只是那个**方向或标签**。而「对不对」恰恰是核对者最容易用力的地方。

本脚本不做判断 —— 它只把这类句子**集中列出来**，让核对者无法漏看。
判断仍要回源，脚本无法替代。

用法：
    python direction_scan.py <课程根目录>            列出全部
    python direction_scan.py <课程根目录> --section 03-gfs
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

# 每条 = (类别, 说明, 正则)
PATTERNS: list[tuple[str, str, str]] = [
    ("方向·放弃/接受", "「放弃 X / 接受 X」——源里到底是达到还是放弃？",
     r"(放弃|接受)了?[^。；\n]{0,24}"),
    ("方向·做/不做", "「不做 X 时 / 有 X 之前 / 之后」——时间或因果顺序可能反",
     r"(不做|没有)[^。；\n]{0,20}(时|之前|之后|以前|以后)"),
    ("方向·多少/快慢", "增减与快慢 —— 确认方向",
     r"(增加|减少|变快|变慢|更快|更慢|更高|更低|更大|更小)[^。；\n]{0,18}"),
    ("归属·谁说的", "把命题归给某份材料或某个讲次 —— 逐条回源确认标签",
     r"(幻灯片|教材|讲义|论文|笔记|第 ?\d+ ?讲|第 ?\d+ ?节)[^。；\n]{0,26}"
     r"(说|写|讲|认为|指出|强调|给出|列|记)"),
    ("归属·我们补的", "声明「这是我们的推断/补充」—— 检查是否也落在图内可见文字与 alt",
     r"(我们的|自己)(推断|理解|化简|补充|归纳|换算|叫法|表述)"),
    ("绝对化·唯一/只", "「唯一 / 只有 / 只」——源是否真这么绝对？",
     r"(唯一的?|只有|唯一的|仅仅|只能)[^。；\n]{0,22}"),
    ("绝对化·一定/总是", "「一定 / 总是 / 从来 / 完全」——阈值类主张最易放大",
     r"(一定|必然|总是|从来|永远|完全|全是|绝不)[^。；\n]{0,20}"),
    ("因果·归因", "「因为 / 导致 / 所以」——源说的是因果还是并列？",
     r"[^。；\n]{0,16}(导致|造成了|因而|才导致)[^。；\n]{0,20}"),
    ("对比·不是而是", "「不是 A 而是 B」——两边都可能被调换",
     r"不是[^。；\n]{0,22}而是"),
    # ★ 「空间指涉」—— 附录四要求的那一类，此前只在文档里、脚本里没有。
    #
    # mit65840-author 实测发现：`quality-audit.md` 附录四写着「已加入扫描器的
    # 『空间指涉』类别」，而脚本源码里一处都搜不到（它 grep 了 `空间|最左|最上面`），
    # 扫描输出也确实只有 10 类。那一轮它只能**手工 grep** 完成清点。
    #
    # 而这一类正是附录四要防的事：**改了图的方向/行列/元素顺序，
    # 正文里所有指涉「左/右/上/下/第一行」的句子都会静默失效。**
    # 实测事故：`intro-2` 从「三张纵向堆叠卡片」改成「纵向刻度」后，
    # 正文 L131 仍写「最左边那一档」，而同页 L137 自己写着「刻度最上面那一档」。
    ("空间指涉", "「左/右/上/下/最左/第一行/上一格」——改过图的布局方向后，这些句子会静默失效",
     r"(最左边|最右边|最上面|最下面|左列|右列|左半|右半|上排|下排|上排的|下一格|上一格|"
     r"第一行|第二行|第一列|第二列|左边的|右边的|上面的|下面的)[^。；\n]{0,18}"),
    ("因果·顺序与先后", "「先…再…/之后」——步骤顺序或主体可能被写反",
     r"(先|再|然后|接着)[^。；\n]{0,14}(才|再|然后|随后)"),
]

CJK = re.compile(r"[\u4e00-\u9fff]")


def split_front_matter(text: str) -> str:
    parts = text.split("+++", 2)
    return parts[2] if len(parts) == 3 else text


def scan(path: pathlib.Path) -> list[tuple[str, str, int, str, str]]:
    """扫正文与 alt/desc。

    ★ 两个已修的覆盖缺口（由 mit65840-author 用这个工具时实测发现）：

    1. **旧版直接跳过 `![...]` 开头的行** —— 于是 `quality-audit.md` 附录二那条硬规则
       （「我们的化简/推断」这类声明必须同时落在**图内可见文字与 alt**）
       **完全没有被这个扫描器覆盖**。而这正是本项目已经栽过两次的地方
       （`intro-2`、`intro-4` 的 alt 都漏过标记）。
       **alt 恰恰是读屏用户唯一能拿到的东西，所以它必须进扫描范围。**

    2. **旧版用 `re.search`，每行每类只报第一个命中** —— 一行里有两处「放弃/接受」时
       只看得到一处。实测 `raft/index.md` L134 一行里同时有「放弃了…」与「接受了…」，
       只报一个。**已改为 `finditer`，同一行同一类有几个报几个。**
    """
    body = split_front_matter(path.read_text(encoding="utf-8"))
    hits: list[tuple[str, str, int, str, str]] = []
    for i, raw in enumerate(body.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        is_alt = line.startswith("![")
        # alt 行也要扫（附录二）；但它通常较短，所以门槛放宽
        if len(CJK.findall(line)) < (3 if is_alt else 6):
            continue
        for cat, why, pat in PATTERNS:
            for m in re.finditer(pat, line):   # ← finditer：一行多命中全报
                tag = cat + ("·alt" if is_alt else "")
                hits.append((tag, why, i, m.group(0).strip(), line[:110]))
    return hits


def scan_svg_descs(root: pathlib.Path) -> list[tuple[str, str, int, str, str]]:
    """单独扫 SVG 的 <title>/<desc>。

    `direction_scan.py` 只读 `index.md`，而图内可见文字与 `<desc>` 在 `.svg` 里 ——
    附录二要求「正文标了就必须在图内与 alt 各标一次」，那两处**都不在 index.md**。
    所以需要这一趟。
    """
    hits: list[tuple[str, str, int, str, str]] = []
    for svg in sorted((root / "content").rglob("figures/*.svg")):
        t = svg.read_text(encoding="utf-8")
        rel = svg.relative_to(root)
        for tag in ("title", "desc"):
            for m in re.finditer(rf"<{tag}[^>]*>(.*?)</{tag}>", t, re.S):
                txt = re.sub(r"\s+", " ", m.group(1)).strip()
                if len(CJK.findall(txt)) < 3:
                    continue
                ln = t[: m.start()].count("\n") + 1
                for cat, why, pat in PATTERNS:
                    for mm in re.finditer(pat, txt):
                        hits.append((f"{cat}·svg/{tag}", why, ln,
                                     f"{rel}: {mm.group(0).strip()}", txt[:110]))
    return hits



def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="方向词扫描（核对辅助，不做判断）")
    ap.add_argument("root")
    ap.add_argument("--section", default=None, help="只扫指定小节目录名")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    files = sorted((root / "content").rglob("index.md"))
    if args.section:
        # ★ 路径分隔符必须归一化再比。
        #   旧写法是 `args.section in str(f)`，而 Windows 上 str(f) 用**反斜杠**，
        #   于是 `--section papers/mapreduce`（正斜杠）永远匹配不上 ——
        #   **扫了 0 个文件，却打印「合计 0 处」，看起来像一次干净的通过。**
        #   这是 mit65840-author 实测发现的（他用 `--section mapreduce` 得到 39 处，
        #   而 `--section papers/mapreduce` 得到 0 处）。
        #   **一个匹配不到任何文件的过滤器，是「绿灯的理由是错的」的又一个变体。**
        want = args.section.replace("\\", "/").strip("/")
        files = [f for f in files
                 if want in str(f.relative_to(root)).replace("\\", "/")]
        if not files:
            print(f"✗ --section {args.section!r} 没有匹配到任何 index.md。")
            print(f"  这不是「没有问题」，是**过滤器写错了**。")
            print(f"  content/ 下的实际小节：")
            for p in sorted((root / "content").iterdir()):
                if p.is_dir():
                    print(f"    {p.name}")
            return 2

    total = 0
    WHY = {c: w for c, w, _ in PATTERNS}

    def report(label: str, hits: list[tuple[str, str, int, str, str]]) -> int:
        if not hits:
            return 0
        print(f"\n{'=' * 78}\n{label}   （{len(hits)} 处需要回源确认方向/归属）\n")
        by_cat: dict[str, list] = {}
        for cat, why, ln, frag, line in hits:
            by_cat.setdefault(cat, []).append((ln, frag, line))
        for cat in sorted(by_cat):
            base = cat.split("·")[0]
            print(f"  ▸ {cat}")
            print(f"     为什么要看：{WHY.get(base, '')}")
            for ln, frag, line in by_cat[cat]:
                print(f"     L{ln:<4} 命中「{frag[:34]}」")
                print(f"           {line}")
        return len(hits)

    for f in files:
        total += report(str(f.relative_to(root)), scan(f))

    # ★ SVG 的 <title>/<desc> 单独一趟：附录二那两条硬规则管的就是这里，
    #   而它们**不在 index.md 里**，所以只扫正文会整段漏掉。
    if not args.section or True:
        svg_root = root
        if args.section:
            # 只扫该小节下的 figures
            sub = [f for f in files]
            if sub:
                svg_root = sub[0].parent.parent  # content/<section>
                hits = []
                for svg in sorted((svg_root / "figures").glob("*.svg")):
                    t = svg.read_text(encoding="utf-8")
                    for tag in ("title", "desc"):
                        for m in re.finditer(rf"<{tag}[^>]*>(.*?)</{tag}>", t, re.S):
                            txt = re.sub(r"\s+", " ", m.group(1)).strip()
                            if len(CJK.findall(txt)) < 3:
                                continue
                            ln = t[: m.start()].count("\n") + 1
                            for cat, why, pat in PATTERNS:
                                for mm in re.finditer(pat, txt):
                                    hits.append((f"{cat}·svg/{tag}", why, ln,
                                                 f"{svg.name}: {mm.group(0).strip()}", txt[:110]))
                total += report(f"{svg_root.relative_to(root)}/figures/*.svg", hits)
        else:
            total += report("content/**/figures/*.svg（title/desc）", scan_svg_descs(root))

    print(f"\n{'=' * 78}")
    print(f"合计 {total} 处。**这不是错误清单，是必读清单** —— 逐条回源确认方向后再下判定。")
    print("本项目已发生的方向/归属反转：" )
    for t in ("GFS 的 B/T+R×L 归属", "Raft 的「放弃写延迟下界」", "Raft 的陈旧读归因",
              "MapReduce 的「放弃中心化」", "MapReduce 的 combiner 无能为力",
              "6.006 的模块号当讲次号", "CS168 的幻灯片/教材归属"):
        print(f"  · {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
