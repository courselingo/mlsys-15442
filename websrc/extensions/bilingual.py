"""逐段双语对照 —— CourseLingo 的 Markdown 扩展（构建期渲染，输出静态 HTML）。

用法（在任意 Markdown 页面里）：

    :::bilingual zh=bilingual/l01.zh.md en=bilingual/l01.en.md
    :::

两个文件都是**普通 Markdown**，按空行切块后**按位置配对**。
两侧块数不一致时会在页面顶部显式告警，绝不静默错位 ——
对照内容最怕的就是「看起来对上了」。
"""
from __future__ import annotations

import html
import os
import re
from pathlib import Path

import markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.util import AtomicString
from xml.etree import ElementTree as etree

DIRECTIVE_RE = re.compile(r"^:::bilingual\s+zh=(\S+)\s+en=(\S+)\s*$")


def split_blocks(src: str) -> list[str]:
    """按空行切块 —— 与 Markdown 的段落定义一致。"""
    parts = re.split(r"\n[ \t]*\n", src.replace("\r\n", "\n"))
    return [p.strip() for p in parts if p.strip()]


class BilingualProcessor(BlockProcessor):
    def __init__(self, parser, config: dict):
        super().__init__(parser)
        self.config = config
        # 用一个独立实例渲染内层块，避免在同一次解析里递归调用自身
        self._inner = markdown.Markdown(
            extensions=["extra", "sane_lists", "toc", "pymdownx.superfences"],
            output_format="html",
        )

    def test(self, parent, block):
        first = block.split("\n", 1)[0].strip()
        return bool(DIRECTIVE_RE.match(first))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        lines = block.split("\n")
        m = DIRECTIVE_RE.match(lines[0].strip())
        if not m:
            return False

        zh_rel, en_rel = m.group(1), m.group(2)
        # 双语源文件放在 docs/ 之外，免得被 MkDocs 当成页面构建出多余 HTML
        # 路径通过环境变量传入：mkdocs 对扩展的嵌套配置校验很挑剔，绕开它
        base = Path(str(self.config.get("base_dir") or os.environ.get("COURSELINGO_BASE_DIR", ".")))
        zh_path = (base / zh_rel).resolve()
        en_path = (base / en_rel).resolve()

        if not zh_path.is_file():
            self._error(parent, f"找不到中文文件：{zh_rel}")
            return True
        if not en_path.is_file():
            self._error(parent, f"找不到英文文件：{en_rel}")
            return True

        zh_blocks = split_blocks(zh_path.read_text(encoding="utf-8"))
        en_blocks = split_blocks(en_path.read_text(encoding="utf-8"))

        mismatch = len(zh_blocks) != len(en_blocks)
        rows = []
        for i in range(max(len(zh_blocks), len(en_blocks))):
            zh = zh_blocks[i] if i < len(zh_blocks) else ""
            en = en_blocks[i] if i < len(en_blocks) else ""
            rows.append((zh, en, not zh or not en))

        # ---- 组装 HTML ----
        out: list[str] = ['<div class="bi">']

        if mismatch:
            out.append(
                '<p class="bi-warn">⚠️ 两侧段落数不一致'
                f"（中文 {len(zh_blocks)} 段 / 英文 {len(en_blocks)} 段），无法逐段对齐 —— "
                "请补齐后重新构建。</p>"
            )

        for zh, en, bad in rows:
            cls = "bi-row bi-bad" if bad else "bi-row"
            out.append(f'<div class="{cls}">')
            out.append('<div class="bi-cell bi-zh">')
            out.append('<span class="bi-tag">中</span>')
            out.append(
                '<div class="bi-body">'
                + (self._render(zh) if zh else '<p class="bi-empty">（缺中文）</p>')
                + "</div></div>"
            )
            out.append('<div class="bi-cell bi-en">')
            out.append('<span class="bi-tag">EN</span>')
            out.append(
                '<div class="bi-body">'
                + (
                    self._render(en)
                    if en
                    else '<p class="bi-empty">(missing English)</p>'
                )
                + "</div></div>"
            )
            out.append("</div>")

        out.append("</div>")
        raw = "".join(out)

        div = etree.SubElement(parent, "div")
        div.set("class", "bi-host")
        # htmlStash 让这段 HTML 原样输出，不被转义
        div.text = AtomicString(self.parser.md.htmlStash.store(raw))
        return True

    def _render(self, text: str) -> str:
        """用独立实例渲染内层块；每次前 reset，避免状态串台。"""
        self._inner.reset()
        return self._inner.convert(text)

    def _error(self, parent, message: str) -> None:
        div = etree.SubElement(parent, "div")
        div.set("class", "bi-error")
        div.text = f"⚠️ {message}"


class BilingualExtension(Extension):
    # 必须是**类属性** —— Python-Markdown 在实例化之前就要读它来登记配置项
    config = {
        "base_dir": [".", "双语源文件所在目录（通常是课程仓库根目录）"],
    }

    def extendMarkdown(self, md):
        proc = BilingualProcessor(md.parser, self.getConfigs())
        md.parser.blockprocessors.register(proc, "bilingual", 180)


def makeExtension(**kwargs):
    """Markdown 扩展入口（Python-Markdown 按此约定加载）。"""
    return BilingualExtension(**kwargs)
