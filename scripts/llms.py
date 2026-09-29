#!/usr/bin/env python3
"""发布 llms.txt 与每页 Markdown —— 让人和 LLM 都能直接读。

参考对象（GitBook）的做法是：站点除了 HTML，还提供
  * `/llms.txt` —— 全部页面的 Markdown 索引
  * `<page>.html` 旁边再放一份 `<page>.md`
这样 Agent 抓文档时不必解析 HTML。

我们的内容本来就是 Markdown，成本几乎为零：把生成期的 docs/ 复制成 .md，
再把 `:::bilingual` 指令**展开成「中文 / English」交替的可读文本**
（否则 LLM 看到的是一条无法解析的路径指令）。
"""
from __future__ import annotations

import re
from pathlib import Path

DIRECTIVE_RE = re.compile(r":::bilingual\s+zh=(\S+)\s+en=(\S+)\s*\n:::")


def split_blocks(src: str) -> list[str]:
    parts = re.split(r"\n[ \t]*\n", src.replace("\r\n", "\n"))
    return [p.strip() for p in parts if p.strip()]


def expand_bilingual(text: str, base: Path) -> tuple[str, int]:
    """把双语指令展开成中英交替块；返回 (新文本, 展开次数)。"""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        zh_p, en_p = base / m.group(1), base / m.group(2)
        if not (zh_p.is_file() and en_p.is_file()):
            return f"（双语内容缺失：{m.group(1)} / {m.group(2)}）"
        zh = split_blocks(zh_p.read_text(encoding="utf-8"))
        en = split_blocks(en_p.read_text(encoding="utf-8"))
        count += 1
        out = []
        for i in range(max(len(zh), len(en))):
            out.append(f"**中文**\n\n{zh[i] if i < len(zh) else '（缺）'}")
            out.append(f"**English**\n\n{en[i] if i < len(en) else '(missing)'}")
        return "\n\n".join(out)

    return DIRECTIVE_RE.sub(repl, text), count


def emit(
    base: Path,
    docs_dir: Path,
    site_dir: Path,
    site_title: str,
    subtitle: str,
    sections: dict[str, list[tuple[str, str]]],
    about: str,
) -> tuple[int, int]:
    """复制每页 .md 到站点，并写 llms.txt。返回 (页面数, 展开的双语块数)。"""
    pages = 0
    expansions = 0

    for _, items in sections.items():
        for _, rel in items:
            src = docs_dir / f"{rel}.md"
            if not src.is_file():
                continue
            text, n = expand_bilingual(src.read_text(encoding="utf-8"), base)
            expansions += n
            dst = site_dir / f"{rel}.md"
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text, encoding="utf-8")
            pages += 1

    lines = [f"# {site_title}", "", f"> {subtitle}", ""]
    for name, items in sections.items():
        lines.append(f"## {name}")
        lines.append("")
        for title, rel in items:
            lines.append(f"- [{title}]({rel}.md)")
        lines.append("")
    lines.append("## 关于")
    lines.append("")
    lines.append(about.strip())
    lines.append("")
    (site_dir / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    return pages, expansions
