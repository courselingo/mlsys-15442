#!/usr/bin/env python3
"""配图房规检查 —— 调用 vendor 进来的 svg-lint（Node，零依赖）。

房规要求 **0 error 且 0 warning**。默认只把 error 当失败（warning 会打印出来
但不拦截，方便渐进修），加 --strict 则 warning 也拦截 —— CI 用 --strict。

用法：
    python scripts/check_figures.py [--root .] [--strict]

Node 定位顺序：环境变量 COURSELINGO_NODE -> PATH 里的 node。
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

LINT_REL = Path("tools") / "svg-lint" / "bin" / "svg-lint.mjs"


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def find_node() -> str | None:
    env = os.environ.get("COURSELINGO_NODE")
    if env and Path(env).exists():
        return env
    found = shutil.which("node")
    if found:
        return found
    # 本机 DSH 运行时里常见的固定位置
    guess = Path.home() / ".dsh" / "dsh-runtimes" / "dsh-primary-runtime" / "dependencies" / "node" / "bin" / "node.exe"
    return str(guess) if guess.exists() else None


def report_missing_figures(root: Path) -> int:
    """★ 引用了而磁盘上不存在的图（2026-09-29 加，见 quality-audit 附录六十六）。

    起因：mit-6.006 第 10、11 讲各**引用 11 张图**而 figures/ 是空的，而
    **六道门全部通过** —— 因为 `check_figures` 只遍历磁盘上有的图，
    而 `audit_content` 的 IMG 正则只读 markdown、不看文件是否存在。
    ⇒ 于是「所有图都缺失」这个状态落在每一道门的视野之外，而读者看到破图图标。

    ★ 判据的误报率**可证明为 0**：引用了不存在的文件永远是缺陷，没有例外。
    """
    missing: list[str] = []
    orphans: list[str] = []
    for md in sorted(root.glob("content/**/index.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        refs = re.findall(r"\]\((?:\.\./)*figures/([^)\s]+)\)", text)
        fdir = md.parent / "figures"
        present = {p.name for p in fdir.glob("*")} if fdir.is_dir() else set()
        rel = md.relative_to(root).as_posix()
        for name in dict.fromkeys(refs):
            if name not in present:
                missing.append(f"{rel}: 引用了 figures/{name}，而它不在磁盘上")
        # ★★ 反向：磁盘上有、而正文没引用（孤儿图）—— 2026-09-29 补。
        #   起因：两位作者各撞了一次 —— 一位写好 `bitcoin-11.svg` 后**漏跑插入引用的脚本**，
        #   而另一位的生成器在「引了没构建器」时才报错；**而这里原本只查 引用→文件 这一个方向**
        #   ⇒ 于是孤儿图**落在每一道门的视野之外**，而它同时会把密度算低（因为图不计入引用数）。
        #   ★ 误报率为 0：`figures/` 目录里没被任何一节引用的图，永远是缺陷（要么漏引用、要么多余）。
        if refs:
            for name in sorted(present):
                if name not in refs:
                    orphans.append(f"{rel}: figures/{name} 在磁盘上而正文没有引用它（孤儿图）")
    if missing:
        print("\n❌ 引用了而磁盘上不存在的图：")
        for m in missing:
            print(f"   {m}")
        print(f"   ⇒ 共 {len(missing)} 处。读者会看到破图图标。")
    if orphans:
        print("\n❌ 磁盘上有而正文没引用的图（孤儿图）：")
        for o in orphans:
            print(f"   {o}")
        print(f"   ⇒ 共 {len(orphans)} 处。它不显示给读者，而会让密度偏低、并让差集两向失去意义。")
    if missing or orphans:
        return 1
    print("✅ 图片引用与磁盘一致（两个方向都查了：无缺文件、无孤儿图）")
    return 0


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    ap = argparse.ArgumentParser(description="配图房规检查（svg-lint）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true", help="warning 也视为失败")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    linter = root / LINT_REL
    if not linter.exists():
        print(f"⚠️  找不到 {LINT_REL} —— 跳过配图检查（该仓库未 vendor 房规工具）")
        return 0

    figures = sorted((root / "content").rglob("figures/*.svg"))
    if not figures:
        print("配图检查：content/**/figures/ 下没有 SVG —— 跳过")
        return 0

    node = find_node()
    if not node:
        print("⚠️  找不到 node —— 无法运行配图检查。", file=sys.stderr)
        print("   设置 COURSELINGO_NODE 指向 node 可执行文件，或把 node 放进 PATH。", file=sys.stderr)
        return 0

    print(f"配图房规检查：{len(figures)} 张图")
    proc = subprocess.run(
        [node, str(linter), *[str(f) for f in figures]],
        capture_output=True, text=True, encoding="utf-8",
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    # 只保留结论行，避免刷屏；完整输出在有错时打印
    tail = [ln for ln in out.splitlines() if "file(s)" in ln or "WARNINGS" in ln]

    errors = len([ln for ln in out.splitlines() if " error " in ln])
    warnings = len([ln for ln in out.splitlines() if " warning " in ln])

    if errors or (args.strict and warnings):
        print(out)
        print("-" * 68)
        print(f"❌ 配图未过房规：{errors} 个 error，{warnings} 个 warning")
        if args.strict and warnings and not errors:
            print("   （--strict：warning 也拦截）")
        print("   规范见 docs/diagram-conventions.md")
        return 1

    for ln in tail:
        print("  " + ln)
    print(f"✅ 配图通过房规（{errors} error，{warnings} warning）")
    # ★ 房规过了，还要核「引用了而磁盘上没有的图」（附录六十六）
    return max(report_missing_figures(root), 0)


if __name__ == "__main__":
    sys.exit(main())
