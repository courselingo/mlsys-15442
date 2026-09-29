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

    # ★★ 必须**分批**调用 linter。**不要把所有路径塞进一个 argv。**
    #
    # 起因（2026-09-29，`mlsys` 第 21 讲交付时作者报的）：
    #   这门课的图从 46 张长到 **291 张**，而 `argv` 的总长度有上限
    #   （Windows 上 `CreateProcess` 约 32 KB）⇒ 直接抛：
    #       FileNotFoundError: [WinError 206] 文件名或扩展名太长。
    #   **⇒ 第 4 道门禁不是「判了不合格」，而是「自己挂了」。**
    #
    # ★ 而它最阴的地方是**它随规模悄悄失效**：
    #   图少的时候这一行跑得好好的（本会话此前跑这门课它一直是 exit 0），
    #   图多到某个数之后它才第一次抛异常 —— 而抛异常**看起来像门的判定**。
    #   ⇒ 若作者没有用「同一个 linter、同一个 --strict、只改分批」的等价方法复验，
    #     他会以为「配图不合规」，而真相是**闸门本身坏了**。
    #
    # ⇒ 分批大小取得保守（60），并把每批的 error/warning 行数**相加**
    #   —— 语义与一次性调用完全一致（linter 逐文件独立判定，批次之间无耦合）。
    BATCH = 60
    outs: list[str] = []
    errors = 0
    warnings = 0
    for i in range(0, len(figures), BATCH):
        chunk = figures[i:i + BATCH]
        proc = subprocess.run(
            [node, str(linter), *[str(f) for f in chunk]],
            capture_output=True, text=True, encoding="utf-8",
        )
        part = ((proc.stdout or "") + (proc.stderr or "")).strip()
        outs.append(part)
        errors += len([ln for ln in part.splitlines() if " error " in ln])
        warnings += len([ln for ln in part.splitlines() if " warning " in ln])

    out = "\n".join(outs).strip()
    # 只保留结论行，避免刷屏；完整输出在有错时打印
    tail = [ln for ln in out.splitlines() if "file(s)" in ln or "WARNINGS" in ln]

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
