#!/usr/bin/env python3
"""新建一个论文页（导读或全文翻译）。

刻意**要求先在 papers.toml 登记** —— 顺序反了就会出问题：
先写稿后补授权，等于把「未授权就翻译」变成既成事实。

用法：
    python scripts/new_paper.py --key mapreduce --title "MapReduce 导读" --mode guide
    python scripts/new_paper.py --key mapreduce --title "MapReduce 全文翻译" --mode translation
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

GUIDE_SKELETON = '''+++
kind = "paper"
paper = "{key}"
title = "{title}"
status = "draft"
output_mode = "guide"
+++

> **这是「导读」，不是翻译。**
> 用我们自己的话讲清楚这篇论文要解决什么问题、怎么解的、代价是什么。
> 不逐句对照原文，也不包含原文段落。
>
> 原始论文：{paper_url}

## 这篇论文要解决什么问题

<!-- 用具体的问题开头，不要复述摘要。说明：当时为什么必须解决它？ -->

## 核心思路

<!-- 讲清楚「为什么这么设计」，而不只是「设计了什么」。 -->

## 它在哪里会碰到麻烦

<!-- 边界情况、失效场景、作者的取舍。这一节往往是导读最有价值的部分。 -->

## 代价

<!-- 这个设计放弃了什么？后来的系统针对哪一点做了改进？ -->

## 读完应该能回答

- <!-- 2–3 个具体问题，读者能自测是否读懂 -->
'''

TRANSLATION_SKELETON = '''+++
kind = "paper"
paper = "{key}"
title = "{title}"
status = "draft"
output_mode = "translation"
+++

> **这是全文翻译。**
> 授权凭据：{evidence}
> 原文：{paper_url}
>
> 本页的 `output_mode = "translation"` 由 `validate.py` 与 `build.py` 双重把关：
> 只要 `papers.toml` 中该篇的 `verified` 或 `allows_translation` 任一为 false，构建就会失败。

## 译者说明

<!-- 标明所依据的版本（会议版 / 扩展版 / 技术报告版）、译者、以及翻译中做的取舍。 -->

'''

TITLE = "title"


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description="新建论文页（须先在 papers.toml 登记）")
    parser.add_argument("--root", default=".", help="课程仓库根目录")
    parser.add_argument("--key", required=True, help="papers.toml 中已登记的 paper key")
    parser.add_argument("--title", required=True, help="本页标题，例如「MapReduce 导读」")
    parser.add_argument("--mode", required=True, choices=["guide", "translation"])
    parser.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    registry = root / "papers.toml"
    if not registry.exists():
        print(f"错误：{root} 下没有 papers.toml", file=sys.stderr)
        return 2
    try:
        with registry.open("rb") as fh:
            papers = tomllib.load(fh).get("paper", [])
    except tomllib.TOMLDecodeError as exc:
        print(f"错误：papers.toml 解析失败：{exc}", file=sys.stderr)
        return 2

    paper = next((p for p in papers if str(p.get("key", "")) == args.key), None)
    if paper is None:
        print(f"错误：{args.key!r} 未在 papers.toml 中登记。", file=sys.stderr)
        print("      请先登记元数据与 [paper.license]，再创建页面 —— 顺序不能反。", file=sys.stderr)
        return 2

    lic = paper.get("license") or {}

    # ★ 政策性拒绝优先：论文明确不允许传播，就不做，也不建页面。
    if lic.get("redistribution") == "forbidden":
        print(f"⛔ 拒绝执行：论文 {args.key!r} 明确不允许传播。", file=sys.stderr)
        print('      [paper.license].redistribution = "forbidden"', file=sys.stderr)
        if str(lic.get("evidence_url", "")).strip():
            print(f"      依据：{lic['evidence_url']}", file=sys.stderr)
        print("      这是政策性拒绝，改内容没有用。见 docs/content-policy.md", file=sys.stderr)
        return 3

    if args.mode == "translation":
        if not (lic.get("verified") is True and lic.get("allows_translation") is True):
            print(f"⛔ 拒绝创建全文翻译页：{args.key!r} 的授权不满足条件。", file=sys.stderr)
            print(
                f"      verified={lic.get('verified')!r}, "
                f"allows_translation={lic.get('allows_translation')!r}",
                file=sys.stderr,
            )
            print("      两个都必须为 true。只「核实过」不够 —— 核实结果可能是「不允许翻译」。", file=sys.stderr)
            print("      见 docs/paper-licensing.md", file=sys.stderr)
            return 2

    key = args.key
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
        print(f"错误：key={key!r} 不合规", file=sys.stderr)
        return 2

    target_dir = root / "content" / "papers" / key
    target = target_dir / "index.md"
    if target.exists() and not args.force:
        print(f"错误：{target} 已存在（用 --force 覆盖）", file=sys.stderr)
        return 2

    skeleton = GUIDE_SKELETON if args.mode == "guide" else TRANSLATION_SKELETON
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(
        skeleton.format(
            key=key,
            title=args.title,
            paper_url=str(paper.get("url", "")) or "（papers.toml 中未填 url）",
            evidence=str(lic.get("evidence_url", "")) or "（未填 evidence_url —— 请补上）",
        ),
        encoding="utf-8",
    )
    (target_dir / "figures").mkdir(exist_ok=True)

    print(f"已创建：{target.relative_to(root)}")
    print(f"  论文：{paper.get('title', '')}  ({paper.get('venue', '')})")
    print(f"  模式：{args.mode}")
    if args.mode == "guide":
        print("  提醒：导读的价值在于「讲明白」，不要退化成摘要或逐段改写。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
