#!/usr/bin/env python3
"""文风机检 —— 把「反 AI 味」变成可执行的闸门。

规范见 docs/writing-style.md。可机检的部分全部在这里实现；
机检不了的（讲得清不清楚）不在这里假装能查。

退出码：0 通过 / 1 有违规 / 2 用法或 IO 错误
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")

# ---- 硬拦词：出现即失败 ----
BANNED = {
    "空洞总起": ["在当今", "随着", "众所周知", "不难发现", "显而易见", "众所周知"],
    "空洞收尾": ["综上所述", "总而言之", "总的来说", "希望本文", "让我们一起"],
    "营销腔": [
        "深入浅出", "一探究竟", "揭秘", "全景", "硬核", "干货", "赋能",
        "抓手", "闭环", "底层逻辑", "范式", "生态位",
    ],
    "空转铺垫": ["本文将带你", "接下来我们将", "下面让我们", "值得一提的是", "需要注意的是"],
}
# 「维度」「生态」单用可能是正常技术词，只在配合营销腔时才算 —— 这里保守处理
SOFT_MARKETING = ["维度", "生态"]

MECHANICAL_OPENERS = ["首先，", "其次，", "再次，", "最后，"]
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]"
)

TITLE_RE = re.compile(r"^\s{0,3}(#{2,3})\s+(.+?)\s*$", re.M)


def force_utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def split_front_matter(text: str) -> str:
    parts = text.split("+++", 2)
    return parts[2] if len(parts) == 3 else text


def strip_markup(body: str) -> str:
    """去掉代码块/行内代码/标记，避免把代码当成正文统计。"""
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = re.sub(r"`[^`]*`", " ", body)
    body = re.sub(r"\[\[term:[^\]]+\]\]", "术语", body)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    return body


def check(path: Path) -> list[str]:
    body = split_front_matter(path.read_text(encoding="utf-8"))
    plain = strip_markup(body)
    n_cjk = len(CJK.findall(plain))
    if n_cjk < 400:
        return []
    problems: list[str] = []
    per_k = max(n_cjk / 1000.0, 0.001)

    # 硬拦词
    for cat, words in BANNED.items():
        hits = []
        for w in dict.fromkeys(words):
            c = plain.count(w)
            if c:
                hits.append(f"{w}×{c}")
        if hits:
            problems.append(f"[{cat}] " + "、".join(hits))

    # 机械分段：段首序数词超过 4 次
    mo = sum(plain.count(w) for w in MECHANICAL_OPENERS)
    if mo > 4:
        problems.append(f"[机械分段] 段首「首先/其次/再次/最后」共 {mo} 次（>4）")

    # 破折号
    dash = plain.count("——")
    if dash / per_k > 1.0:
        problems.append(f"[破折号] {dash} 处 / {per_k:.1f}k 字（阈值 1.0）")

    # 加粗
    bold = len(re.findall(r"\*\*[^*]+\*\*", plain))
    if bold / per_k > 4.0:
        problems.append(f"[加粗] {bold} 处 / {per_k:.1f}k 字（阈值 4.0 = 1/250 字）")

    # 不是…而是…
    nzb = len(re.findall(r"不是[^，。；\n]{0,30}而是", plain))
    if nzb > 2:
        problems.append(f"[不是…而是…] {nzb} 处（阈值 2）")

    # 设问
    q = len(re.findall(r"[？?]", plain))
    if q > 4:
        problems.append(f"[设问] 问号 {q} 处（阈值 4）")

    # emoji
    if EMOJI.search(plain):
        problems.append("[emoji] 正文出现 emoji")

    # 超长段落
    long_paras = [i for i, p in enumerate(body.split("\n\n"), 1) if len(p.splitlines()) > 8
                  and len(CJK.findall(p)) > 200]
    if long_paras:
        problems.append(f"[段落过长] 第 {long_paras[:3]} 段超过 8 行且 >200 字")

    # 脉络锚点：开头段 + 收束段
    if not re.search(r"(要解决|解决什么|为什么需要|痛点|背景)", plain[:1200]):
        problems.append("[脉络] 开头 1200 字内没有「这一讲要解决什么」的痛点交代")

    # ★ 收束段检查：必须是一个**有实体的收尾小节**，不能靠尾段里出现一个关键词蒙过去。
    #
    # 旧写法是 `re.search(r"(回顾|小结|脉络|串起来|回到)", plain[-1500:])`，有一个真实漏洞：
    # **只要在最后一段里塞进「串起来」三个字就能通过。**
    # 2026-09-28 一次独立复核对 CS168 第 1 讲实测到：满足该检查的正是新补的收束句
    # （`串起来` 在 index 5472），而它真正的回顾段落在 index 4785，**在窗口之外** ——
    # 也就是说那道机检**通过了，但通过的理由是错的**。
    #
    # 一个能被一个词满足的闸门是弱闸门，而且会诱发「补关键词」这种假通过。
    # 新写法要求两件事，都与措辞无关：
    #   1. 末尾 TAIL 字内存在一个小节标题（任意命名，不强制叫「小结」——命名不该进闸门）
    #   2. 该小节正文不少于 MIN_TAIL_CJK 个汉字（排除「空标题」）
    # 它拦的是真实失败模式：**页面在段落后草草收尾，没有收束小节**。
    TAIL, MIN_TAIL_CJK = 2000, 100
    heads = [(m.start(), m.end(), m.group(2).strip())
             for m in re.finditer(r"(?m)^(#{2,4})[ \t]+(.+?)[ \t]*$", plain)]
    closing = [(s, e, t) for s, e, t in heads if s >= len(plain) - TAIL]
    if not closing:
        problems.append(f"[脉络] 末尾 {TAIL} 字内没有任何小节标题，页面像在段落里草草收尾")
    else:
        s, _e, title = closing[0]
        nxt = next((h[0] for h in heads if h[0] > s), len(plain))
        body_cjk = len(CJK.findall(plain[s:nxt]))
        if body_cjk < MIN_TAIL_CJK:
            problems.append(
                f"[脉络] 收尾小节「{title}」正文只有 {body_cjk} 汉字（需 ≥{MIN_TAIL_CJK}），"
                f"像是为了过检查补的空标题")
    # ★ 刻意**不检查收尾小节的标题用词**。
    #
    # 我第一版加了一条「标题里要有回顾/小结/收束等词」的提示，并以为它是非阻断的 ——
    # 结果它照样进了 problems、照样让 exit=1，一上来就把 6 篇**本来收尾很正常**的页面判红：
    #   「代价与边界」「这套设计付出了什么」「幂等：让重试变得安全」…
    # 这些标题都是合理的收尾小节，逼它们改名去凑关键词表，
    # **正是我刚刚批评旧闸门的那种毛病**（靠关键词表判「有没有回顾」，拦不住蒙混、还误伤好写法）。
    #
    # 所以标题用词不进闸门。要管的只有结构：**页面末尾有没有一个像样的收束小节**。


    return problems


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    ap = argparse.ArgumentParser(description="文风机检")
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true", help="保留参数；本检查默认即拦截")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    files = sorted((root / "content").rglob("index.md"))
    if not files:
        print("文风机检：content/ 下没有 index.md —— 跳过")
        return 0

    print(f"文风机检：{len(files)} 篇")
    bad = 0
    for f in files:
        probs = check(f)
        rel = f.relative_to(root).as_posix()
        if probs:
            bad += 1
            print(f"\n  ❌ {rel}")
            for p in probs:
                print(f"       {p}")
        else:
            print(f"  ✅ {rel}")
    print()
    if bad:
        print(f"❌ {bad} 篇未过文风检查。规范见 docs/writing-style.md")
        return 1
    print("✅ 文风检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
