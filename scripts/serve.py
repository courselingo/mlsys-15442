#!/usr/bin/env python3
"""本地预览服务器 —— 生成站点 + 起 MkDocs 实时预览 + 内容改动自动重生成。

为什么需要它（而不是直接 mkdocs serve）：
  MkDocs 只认识它自己的 `docs/`，而我们的**内容真相在 `content/`**。
  `docs/` 是 build_site.py 生成的中间产物。
  所以直接 `mkdocs serve` 时，你改 `content/*.md` 浏览器不会有任何反应 ——
  必须有人重新跑一遍生成。这个脚本就是那个人：它盯着 `content/`，
  一有改动就重跑生成，MkDocs 自己的 watcher 再把页面刷新出去。

用法：
    python scripts/serve.py                 # 默认 127.0.0.1:8765
    python scripts/serve.py --port 9000
    python scripts/serve.py --no-watch      # 只生成并起服务，不监听改动

已知限制（MkDocs 的机制所限，非本脚本的缺陷）：
    `llms.txt` 与每页的 `.md` 孪生文件**在预览里取不到**。
    原因是 MkDocs 把 docs/ 里的 `.md` 一律当**页面**编译成 HTML，
    不会保留原始 Markdown；这两个产物是构建完成后再写进 site_dir 的，
    因此只在 `build_site.py` 的静态产物里存在（也就是部署出去的那份）。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import time
from pathlib import Path

# 要监视的**源**路径。
#
# ⚠️ 绝不能写 "websrc" 整个目录 —— 生成器会把产物写进 websrc/docs 与
#    websrc/mkdocs.yml，监视它就会「生成→触发→再生成」无限循环。
#    只盯 websrc 下的**源**文件（assets / extensions），不盯产物。
WATCH = [
    "content",
    "bilingual",
    "glossary.toml",
    "papers.toml",
    "course.toml",
    "websrc/assets",
    "websrc/extensions",
]
POLL_SECONDS = 1.5


def force_utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def snapshot(root: Path) -> dict[str, float]:
    """记录被监视路径的 mtime，用于判断是否发生改动。"""
    state: dict[str, float] = {}
    for name in WATCH:
        p = root / name
        if p.is_file():
            state[str(p)] = p.stat().st_mtime
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and "__pycache__" not in f.parts:
                    state[str(f)] = f.stat().st_mtime
    return state


def generate(root: Path) -> bool:
    """跑一次 build_site.py（它内含授权闸门）。返回是否成功。"""
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "build_site.py"), "--root", str(root)],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if proc.returncode != 0:
        print("\n" + "=" * 68)
        print(f"⛔ 生成失败（退出码 {proc.returncode}）—— 站点未更新")
        print("=" * 68)
        print(out[-1800:])
        return False
    for line in out.splitlines():
        if any(k in line for k in ("校验通过", "构建完成", "入口", "已发布", "[!]", "警告")):
            print("   " + line)
    return True


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    ap = argparse.ArgumentParser(description="CourseLingo 本地预览")
    ap.add_argument("--root", default=".")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-watch", action="store_true", help="不监听内容改动")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "websrc").is_dir():
        print(f"错误：{root} 下没有 websrc/ —— 这不是一个 MkDocs 化的课程仓库", file=sys.stderr)
        return 2

    print("① 生成站点")
    if not generate(root):
        return 1

    cfg = root / "websrc" / "mkdocs.yml"
    if not cfg.exists():
        print(f"错误：{cfg} 未生成", file=sys.stderr)
        return 1

    if not args.no_watch:
        def watcher() -> None:
            last = snapshot(root)
            while True:
                time.sleep(POLL_SECONDS)
                cur = snapshot(root)
                if cur != last:
                    changed = [k for k in cur if last.get(k) != cur.get(k)]
                    last = cur
                    names = ", ".join(Path(c).name for c in changed[:4])
                    print(f"\n↻ 检测到改动（{names}）—— 重新生成")
                    generate(root)

        threading.Thread(target=watcher, daemon=True).start()

    print(f"\n② 启动预览：http://{args.host}:{args.port}/")
    print("   Ctrl+C 停止\n")
    # 必须把与 build_site.py **相同**的环境传给 mkdocs：
    #   PYTHONPATH  —— 否则 `extensions.bilingual` 这个自定义扩展 import 不到
    #   COURSELINGO_BASE_DIR —— 双语源文件不在 docs/ 里，扩展要知道去哪找
    import os
    env = {
        **os.environ,
        "PYTHONPATH": str(root / "websrc"),
        "COURSELINGO_BASE_DIR": str(root),
        "PYTHONIOENCODING": "utf-8",
    }
    try:
        return subprocess.call(
            # 预览**不加 --strict**：编辑过程中出现一个告警就整站挂掉，对审阅体验很糟。
            # --strict 留给 CI 与 build_site.py，那才是该拦截的地方。
            [sys.executable, "-m", "mkdocs", "serve",
             "-f", str(cfg), "-a", f"{args.host}:{args.port}"],
            cwd=str(root), env=env,
        )
    except KeyboardInterrupt:
        print("\n已停止。")
        return 0


if __name__ == "__main__":
    sys.exit(main())
