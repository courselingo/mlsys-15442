#!/usr/bin/env python3
"""新建一讲。

用法：
    python scripts/new_lecture.py --title "Raft 领导者选举" --slug raft-leader-election \
        --source-url "https://example.org/lec/05" --source-title "Raft (part 2)"

会在 content/<NN>-<slug>/index.md 生成骨架，NN 自动取当前最大讲次 + 1。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


SKELETON = '''+++
title = "{title}"
lecture = {lecture}
slug = "{slug}"
status = "draft"
source_kind = "{kind}"
source_url = "{source_url}"
source_title = "{source_title}"
output_mode = "explanation"
+++

> 本讲是 CourseLingo 的**原创中文讲解**，不是原文翻译。
> 授权状态见 `course.toml` 的 `[license]` 段；未核实前不得改写为逐字稿。

## 这一讲要解决什么问题

<!-- 用一两句话说明：学完这一讲，读者能回答什么问题。
     不要复述课程简介，直接给问题。 -->

## 开始之前需要知道

<!-- 概念前置：列出读者需要但原文默认已知的背景知识。
     引用术语请用 [[term:key]]，key 来自 glossary.toml。 -->

## 核心思路

<!-- 讲清楚「为什么这么做」，而不只是「做了什么」。
     关键推导不要跳步。 -->

## 代码

<!-- 代码要有中文注释，只解释关键行，不要整块照抄。 -->

```text
（在此粘贴代码）
```

## 小结

<!-- 三到五条，能独立看懂。 -->
'''

TITLE = "title"


def next_lecture_number(content_dir: Path) -> int:
    biggest = 0
    if content_dir.is_dir():
        for p in content_dir.iterdir():
            m = re.match(r"^(\d+)-", p.name)
            if m:
                biggest = max(biggest, int(m.group(1)))
    return biggest + 1


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description="新建一讲")
    parser.add_argument("--root", default=".", help="课程仓库根目录")
    parser.add_argument("--title", required=True, help="中文标题")
    parser.add_argument("--slug", required=True, help="英文 slug（小写连字符）")
    parser.add_argument("--source-url", default="", help="原始出处 URL")
    parser.add_argument("--source-title", default="", help="原始出处标题")
    parser.add_argument("--kind", default="notes", choices=["notes", "video", "textbook", "slides", "other"])
    parser.add_argument("--lecture", type=int, default=0, help="讲次（默认自动 +1）")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "course.toml").exists():
        print(f"错误：{root} 下没有 course.toml（这里不是课程仓库）", file=sys.stderr)
        return 2

    slug = args.slug.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        print(f"错误：slug={slug!r} 不合规（只允许小写字母、数字与连字符）", file=sys.stderr)
        return 2

    content_dir = root / "content"
    lecture = args.lecture or next_lecture_number(content_dir)
    target_dir = content_dir / f"{lecture:02d}-{slug}"
    target = target_dir / "index.md"

    if target.exists() and not args.force:
        print(f"错误：{target} 已存在（用 --force 覆盖）", file=sys.stderr)
        return 2

    if not args.source_url:
        print("提示：未提供 --source-url，front matter 会留下空值，validate.py 将报错。")

    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(
        SKELETON.format(
            title=args.title, lecture=lecture, slug=slug, kind=args.kind,
            source_url=args.source_url, source_title=args.source_title or args.title,
        ),
        encoding="utf-8",
    )
    (target_dir / "figures").mkdir(exist_ok=True)

    print(f"已创建：{target.relative_to(root)}")
    print(f"  讲次 {lecture}  ·  slug {slug}")
    print("  下一步：填 front matter 的 source_url，再到 glossary.toml 补本讲需要的术语")
    return 0


if __name__ == "__main__":
    sys.exit(main())
