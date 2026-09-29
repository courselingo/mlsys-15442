#!/usr/bin/env python3
"""派活前检查：这一页的「证据」到底在不在磁盘上。

## 起因

task-15（04-paxos）的任务书里写着「逐条见核对报告」，而那份报告**磁盘上不存在** ——
它是子代理报给 Lead 的一条消息。执行者只有两条路：猜，或者停下来问。
它停下来问了，**但那多花了一轮**。

`mit65840-author` 建议把这条做成机检：「任务书里每个『见…报告』都对应一个存在的路径」。

**但那条检查在 `validate.py` 里做不了** —— 任务书是通过共享任务板下发的，
**不在仓库里，`validate.py` 看不见它**。
（这本身又是一次「接口两端各说各话」：建议的检查点和被检查的东西不在同一个地方。）

## 所以这个脚本检查的是**可检查的那一半**

派活前，证据必须已经在磁盘上：

  · 这一页有没有**事实核对报告**？（`docs/audit/<page>-factcheck.md` 或等价命名）
  · 这一页有没有**质量审核记录**？（§9 要求的那份）
  · 该页的配图有没有**视觉复核报告**？

**只要这三样里有一样缺失，任务书就不该引用它。**

用法：
    python check_evidence.py --root <课程根目录>            # 全部页面
    python check_evidence.py --root <课程根目录> --page 04-paxos
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

# 论文页在 content/papers/<name>/，课程页在 content/<slug>/
NAME_RE = re.compile(r"^(\d+)-(.+)$")


def norm(s: str) -> str:
    return re.sub(r"[-_]", "", s).lower()


def look(ad: pathlib.Path, page_dir: str) -> dict[str, list[str]]:
    """按三种命名习惯找这一页的记录（与 check_reviewed.py 同一套匹配）。"""
    out: dict[str, list[str]] = {"factcheck": [], "quality": [], "other": []}
    if not ad.exists():
        return out
    stem = page_dir
    num = NAME_RE.match(page_dir)
    num = num.group(1) if num else ""
    ss = norm(stem)
    for f in sorted(ad.glob("*.md")):
        fs = norm(f.stem)
        hit = ss and ss in fs
        if not hit and num:
            hit = bool(re.search(rf"(?<!\d)0*{num}(?!\d)", f.stem))
        if not hit:
            t = f.read_text(encoding="utf-8", errors="replace")
            hit = any(stem in ln or page_dir in ln
                      for ln in t.splitlines() if ln.lstrip().startswith("#"))
        if not hit:
            continue
        low = f.stem.lower()
        if "factcheck" in low or "核对" in low or "事实" in low:
            out["factcheck"].append(f.name)
        elif "quality" in low or "audit" in low or "质量" in low or "审核" in low:
            out["quality"].append(f.name)
        else:
            out["other"].append(f.name)
    return out


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="派活前检查证据是否在磁盘上")
    ap.add_argument("--root", required=True)
    ap.add_argument("--page", default=None, help="只看某一页（目录名，如 04-paxos）")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    content = root / "content"
    ad = root / "docs" / "audit"
    vdir = root.parent.parent / "preview" / "visual-review"

    pages = []
    for p in sorted(content.rglob("index.md")):
        rel = p.parent.relative_to(content).as_posix()
        if rel.startswith("papers/"):
            rel = rel.split("/", 1)[1]
        if args.page and rel != args.page:
            continue
        pages.append((rel, p))

    if not pages:
        print(f"✗ 没找到页面（--page {args.page!r}？）")
        return 2

    missing_any = False
    for rel, p in pages:
        got = look(ad, rel)
        figs = sorted((p.parent / "figures").glob("*.svg"))
        n_vis = sum(1 for f in figs
                    if (vdir / f"{root.name}__{f.stem}.md").exists())
        print(f"=== {rel} ===")
        print(f"  事实核对报告 : {'、'.join(got['factcheck']) if got['factcheck'] else '❌ 无'}")
        print(f"  质量审核记录 : {'、'.join(got['quality']) if got['quality'] else '❌ 无'}")
        print(f"  其他记录     : {'、'.join(got['other']) if got['other'] else '—'}")
        print(f"  配图复核     : {n_vis}/{len(figs)} 张有报告"
              + ("  ❌" if figs and n_vis < len(figs) else ""))
        if not got["factcheck"]:
            missing_any = True
            print("  ⚠️ 派活前注意：**若任务书要引用「核对报告」，它不存在。**")
            print("     → 要么先产出并落盘，要么在任务书里直接给出判据，不要写「见核对报告」。")
        print()

    if missing_any:
        print("⚠️ 有页面缺事实核对报告。**这不代表不能派活** ——")
        print("   只代表任务书里不许引用一份不存在的报告（见 quality-audit.md 附录九）。")
        return 0
    print("✅ 每页的事实核对报告都在磁盘上")
    return 0


if __name__ == "__main__":
    sys.exit(main())
