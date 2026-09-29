#!/usr/bin/env python3
"""页面顶部的授权提示条。

为什么单独一个模块：这些文字会出现在每一个页面上，措辞必须只有一处真相。
renderer 换了，提示条不能跟着丢 —— 读者有权在正文之前就知道授权状态。

★★ 绝不硬编码具体课程的事实 ★★
第一版把「课程主页标注 CC BY 3.0 US，但该徽章只出现在主页；笔记文件
notes/l01.txt 没有声明……」写成了常量 —— 那是 **6.824 的事实**，
却会被贴到**任何** verified != true 的课程**每一页**上。
对 6.006 或 CS168 来说，那是纯虚假陈述，而授权声明写错是本项目最不该犯的错。
现在全部由 course.toml 的 [license] 推导。
"""
from __future__ import annotations

MATERIAL_LABELS = {
    "textbook": "教材",
    "notes": "讲义",
    "slides": "幻灯片",
    "video": "视频",
    "labs": "实验",
    "assignments": "作业",
    "other": "其他材料",
}

COURSE_FORBIDDEN = """!!! danger "本课程授权明确不允许传播"
    按内容策略，本站不发布该课程的任何材料或其衍生内容。
"""

PAPER_NO_TRANSLATION = """!!! note "授权：未核实，或条款未明确允许全文翻译"
    本篇是 CourseLingo 自己撰写的**导读**，不含原论文段落，也不是逐句对照。
    论文的权利归出版方所有，我们只提供链接与自己的解读。
"""


def _names(keys) -> str:
    return "、".join(MATERIAL_LABELS.get(k, k) for k in keys)


def course_banner(license_: dict) -> str:
    """按 course.toml 的 [license] 推导提示条；状态正常时返回空串。"""
    lic = license_ or {}

    if str(lic.get("redistribution")).lower() == "forbidden":
        return COURSE_FORBIDDEN

    terms = str(lic.get("terms", "")).strip()
    evidence = str(lic.get("evidence_url", "")).strip()
    extra = str(lic.get("banner_extra", "")).strip()
    mats = lic.get("materials") or {}

    # ---- ① 整门课未核实 ----
    if lic.get("verified") is not True:
        found = f"我们从上游找到的授权线索：{terms}。" if terms else "上游未给出明确的许可声明。"
        ev = f"\n    {evidence}" if evidence else ""
        body = (
            '!!! warning "本课程授权状态：未核实"\n'
            f"    {found}{ev}\n"
            "\n"
            "    该声明的**覆盖范围未获确认** —— 上游可能在主页给出许可，"
            "而讲义、幻灯片、作业等子页面并无声明。\n"
            "\n"
            "    因此本站**只发布 CourseLingo 自己的原创讲解**：讲概念、不转载原文，"
            "也不提供逐字稿与双语原文对照。\n"
        )
        if extra:
            body += f"\n    {extra}\n"
        return body

    # ---- ② 整门课已核实，但材料是逐项判定的 ----
    allowed = [k for k, v in mats.items() if v is True]
    denied = [k for k, v in mats.items() if v is not True]
    if not denied:
        return ""  # 全部材料都已核实 → 无需提示条

    lines = ['!!! note "本课程授权范围：部分材料已核实"']
    lines.append(f"    ✅ 已核实可用的材料：{_names(allowed)}。" if allowed
                 else "    ⚠️ 尚未核实任何材料。")
    lines.append("")
    lines.append(
        f"    ⛔ {_names(denied)} **未找到许可声明**，覆盖范围未获确认。"
        "这部分本站**只发布原创讲解**，不转载原文、不做逐字稿与双语对照。"
    )
    if terms:
        lines.append("")
        lines.append(f"    已核实部分的许可：{terms}。")
    if evidence:
        lines.append(f"    {evidence}")
    if extra:
        lines.append("")
        lines.append(f"    {extra}")
    return "\n".join(lines) + "\n"


def paper_banner(lic: dict | None) -> str:
    """论文页提示条：未取得翻译许可时说明这是导读。"""
    if not lic:
        return PAPER_NO_TRANSLATION
    if lic.get("verified") is True and lic.get("allows_translation") is True:
        return ""
    return PAPER_NO_TRANSLATION
