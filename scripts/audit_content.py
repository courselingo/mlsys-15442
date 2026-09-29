#!/usr/bin/env python3
"""内容审计 —— 把「质量」里可机检的部分变成闸门。

与另外两道闸门的分工：
  validate.py       授权与术语（合规）
  check_style.py    文风与反 AI 味（句子层面）
  check_figures.py  单张 SVG 的房规（图本身画得对不对）
  **audit_content.py  页面结构与内容密度（该有的有没有）**  ← 本文件

本文件查的是「该画的图画了没、该讲的讲了没」这类**结构性问题**：
配图密度与分布、每个小节是否配图、句子长度、具体性、脉络完整性。

退出码：0 通过（可能带 WARN）/ 1 有 ERROR / 2 用法或 IO 错误
用法：python scripts/audit_content.py [--root .] [--strict]
      --strict 让 WARN 也算失败（CI 用）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
H2 = re.compile(r"^##\s+(.+)$", re.M)
IMG = re.compile(r"!\[[^\]]*\]\((figures/[^)]+\.svg)\)")
CODE = re.compile(r"```.*?```", re.S)

# ---- 阈值（改这里就是改标准）----
MIN_FIG_PER_K = 1.2      # 每千汉字图数下限（红线）
TARGET_FIG_PER_K = 1.8   # 参考目标（**不作闸门**，见下方说明）
MAX_FIG_PER_K = 2.8      # 上限：超过就是拿图凑数

# ★ 真正决定密度的是「每节几张」，不是「每千字几张」。
#   实测第一轮：每节平均 3.02 张，22 个小节 ≥3 张，最极端 11 张。
#   图文重复度却都在 0.64 以下 —— 说明问题不是「图在复述正文」，
#   而是**同一个机制被切成太多张**。所以限制按节来。
# ★ 为什么密度**下限**不当闸门：
#   用户抱怨的失败模式是「图太多」，所以上限必须硬。
#   而「图太少」已经被「每个内容小节 ≥1 张」覆盖 —— 再设密度下限是冗余的，
#   而且冗余约束会在「小节少而长」的页面上和上限直接打架：实测
#   mapreduce（5 节 / 6981 字）按每节上限只有 12 张，密度 1.72 < 1.8 → 无解。
#   度量互相矛盾时，应当删掉冗余的那一条，而不是让执行者去凑数。
#   TARGET 仅作参考输出，不影响退出码。
MAX_FIG_PER_SECTION = 2      # 【已降级为参考】见下方 MIN_FIG_GAP_CJK；不再作为闸门
LONG_SECTION_CJK = 1500      # 【已降级为参考】同上
MIN_FIG_GAP_CJK = 250        # 同一节里两张图平均不得近于每 250 汉字一张（防挤成一堆）
MAX_GAP_CJK = 1200       # 连续多少汉字无图算「缺口」
MAX_SENT_CJK = 120       # 单句最长汉字数
MAX_SENT_AVG = 55        # 平均句长
MIN_NUM_PER_K = 1.5      # 每千汉字具体数字/量词数
MIN_NAMED_SYSTEMS = 5    # 每页点名的系统/协议数
MIN_TERMS = 8            # [[term:]] 标记数下限
MAX_SAME_LAYOUT = 0.15   # 同一版面指纹最多占全部图的比例（超过 WARN）
LAYOUT_HARD = 0.25       # 超过这个比例判 ERROR（视觉通道失效）
MIN_H2 = 5               # 小节数下限

# 默认名单只是**兜底**，不是标准答案：它偏分布式系统，因为本项目的第一个
# 课程是 MIT 6.824。算法课、机器学习系统课各有自己的「具体对象」，
# 所以真正的名单由 course.toml 的 [audit].named_systems 追加 ——
# 域相关的启发式不该写死在通用脚本里。
DEFAULT_SYSTEMS = [
    "GFS", "MapReduce", "Raft", "Paxos", "ZooKeeper", "Spanner", "Chubby",
    "HDFS", "Ceph", "Dynamo", "BigTable", "Kafka", "etcd", "Memcached",
    "Aurora", "Frangipani", "CRAQ", "Chain Replication", "VMware FT",
    "gRPC", "Thrift", "NFS", "AFS", "xv6", "Go", "RPC", "ZAB", "Multi-Paxos",
    # 跨领域也算得上的通用工具与语言，避免非系统课被误判
    "Python", "Java", "C++", "Rust", "SQLite", "PostgreSQL", "Linux",
    "Docker", "Kubernetes", "Redis", "SQL", "HTTP", "TCP", "JSON",
]


def load_audit_config(root: Path) -> dict:
    """读 course.toml 的 [audit]（named_systems / named_systems_min）。"""
    cfg = root / "course.toml"
    if not cfg.exists():
        return {}
    try:
        import tomllib
        return tomllib.loads(cfg.read_text(encoding="utf-8")).get("audit", {}) or {}
    except Exception:
        return {}


def systems_for(root: Path) -> tuple[list[str], int]:
    c = load_audit_config(root)
    extra = [str(x) for x in (c.get("named_systems") or [])]
    minimum = int(c.get("named_systems_min", MIN_NAMED_SYSTEMS))
    return DEFAULT_SYSTEMS + extra, minimum


def force_utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def strip_fm(text: str) -> str:
    parts = text.split("+++", 2)
    return parts[2] if len(parts) == 3 else text


def sentences(body: str) -> list[str]:
    """按中文句末标点切句，忽略代码块。"""
    t = CODE.sub(" ", body)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    parts = re.split(r"[。！？；\n]+", t)
    return [p.strip() for p in parts if CJK.search(p)]


def audit(path: Path, root: Path, systems: list[str] | None = None,
          named_min: int = MIN_NAMED_SYSTEMS) -> tuple[list[str], list[str]]:
    """返回 (errors, warnings)。"""
    raw = path.read_text(encoding="utf-8")
    body = strip_fm(raw)
    rel = path.relative_to(root).as_posix()
    errs: list[str] = []
    warns: list[str] = []

    n_cjk = len(CJK.findall(body))
    if n_cjk < 300:
        return errs, warns

    per_k = n_cjk / 1000.0
    imgs = list(IMG.finditer(body))
    n_img = len(imgs)
    h2s = H2.findall(body)

    # ---- A. 配图密度 ----
    if n_img / per_k < MIN_FIG_PER_K:
        errs.append(
            f"[配图密度] {n_img} 幅 / {per_k:.1f}k 汉字 = 每千字 {n_img/per_k:.2f} 幅"
            f"（下限 {MIN_FIG_PER_K}，目标 {TARGET_FIG_PER_K}）⇒ 至少还需 "
            f"{int(MIN_FIG_PER_K*per_k)+1-n_img} 幅"
        )
    if n_img / per_k > MAX_FIG_PER_K:
        warns.append(
            f"[配图密度] 每千字 {n_img/per_k:.2f} 幅，超过上限 {MAX_FIG_PER_K}"
            "（图太多会变成幻灯片，且容易凑数）"
        )

    # ---- B. 小节配图覆盖 ----
    if h2s:
        # 每个 H2 到下一个 H2 之间是否有图
        marks = [(m.start(), m.group(1)) for m in H2.finditer(body)]
        for i, (pos, title) in enumerate(marks):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
            seg = body[pos:end]
            # 收尾小节不强制配图
            if re.search(r"(应该能回答|脉络回顾|小结|溯源|来源|延伸阅读)", title):
                continue
            n_here = len(IMG.findall(seg))
            if n_here == 0:
                errs.append(f"[小节缺图] 「{title[:28]}」整节没有配图")
            else:
                # ★ 2026-09-28 修正：固定张数上限降级成**带间距的松边界**。
                #
                # 旧写法 `n_here > MAX_FIG_PER_SECTION(+1)` 是**固定上限**。它当初防的是
                # 「每节堆四五张碎图」（第一轮每节平均 3.02 张、最极端两节各 11 张），
                # 但多轮校对后它开始**惩罚正确性**：内容越诚实越（加归属标注、源文依据、
                # 边界条件）就越长，而固定上限不跟着长 —— GFS 三节余量一度只剩 34–39 个汉字，
                # 作者为压回阈值**删掉了一句源文内容**。
                #
                # 我曾试过「按本节套用全课程的 MAX_FIG_PER_K」，**那个更糟**：
                # 短节只配 1 张图就会超（300 字 + 1 图 = 3.33/千字），三门课立刻全红。
                # 原因是 2.8 是**全课程平均**的上限，不是单节的。
                #
                # 现在用一对**间距**来表达：图和图之间
                #     不小于 MIN_FIG_GAP_CJK（别挤成一堆）
                #     不大于 MAX_GAP_CJK（别让读者久等）
                # 也就是 `n_here ≤ 1 + seg_cjk / MIN_FIG_GAP_CJK`。
                # 这与「单节版式最大同组 ≤1/3」（check_figures 管）合起来，
                # 覆盖了原固定上限想防的两种情形，且**随内容长度自动放宽**。
                seg_cjk = len(CJK.findall(seg))
                cap = 1 + seg_cjk // MIN_FIG_GAP_CJK
                if n_here > cap:
                    errs.append(
                        f"[小节过密] 「{title[:26]}」{seg_cjk} 汉字配了 {n_here} 张图"
                        f"（上限 {cap} 张 ≈ 每 {MIN_FIG_GAP_CJK} 汉字不超过一张）"
                        f"—— 图挤成一堆，应当合并而不是各画一张"
                    )


    # ---- C. 无图缺口 ----
    # ★★ 只量「正文」：把元信息尾巴切掉（2026-09-29 修）
    #   起因：eth-ca 第 11 讲报「(结尾) 附近连续 1413 汉字无图」，
    #   而那一千四百字**全是模板的标准尾巴**（读完应该能回答 / 脉络回顾 / 溯源）——
    #   那三节是元信息（自测题、回顾、溯源），**本来就不该配图**。
    #   而尾段长度是**随讲次增长**的（实测 12 讲：385 → 426 → … → 796 → 1200 → 1413）
    #   ⇒ 这条规则会持续误报，而 10、12 讲已贴着上限。
    #   ★ 而这不是「挪门柱让失败通过」：规则自己的注释写着本意是「别让读者久等」，
    #     那是对**正文**的读者体验要求；而尾巴是我设计的模板，不是正文。
    _tail_m = re.search(
        r"^##\s+.*?(?:读完应该能回答|读完能回答|脉络回顾|溯源|小结)\s*$",
        body, re.M,
    )
    if _tail_m:
        body = body[: _tail_m.start()]
    if imgs:
        prev = 0
        worst = ("", 0)
        for m in imgs:
            if m.start() >= len(body):
                break
            gap = len(CJK.findall(body[prev:m.start()]))
            if gap > worst[1]:
                seg = body[prev:m.start()]
                head = re.search(r"^##\s+(.+)$", seg, re.M)
                worst = (head.group(1) if head else "(开头)", gap)
            prev = m.end()
        tail = len(CJK.findall(body[prev:]))
        if tail > worst[1]:
            worst = ("(结尾)", tail)
        if worst[1] > MAX_GAP_CJK:
            errs.append(
                f"[无图缺口] 「{worst[0][:28]}」附近连续 {worst[1]} 汉字没有图"
                f"（上限 {MAX_GAP_CJK}）"
            )

    # ---- D. 图的上下文（引出句 + 解读句） ----
    # ★★ 解读句必须**限定距离**（2026-09-29 修，由 cs168 作者用证据指出）
    #   旧判据只看「图片之后下一个非空行」⇒ 删掉解读句后，「下一个非空行」是**后面的正文**
    #   ⇒ 它照样通过 ⇒ 只在「图片后紧跟标题或文档结尾」时才报（= 各讲最后一张图）。
    #   实测：临时删掉某页第一张图后的解读句，旧判据报 `ERROR 0 / WARN 0`。
    #   新判据：图片行之后，到**下一个 `##` 标题或下一张图**之间的汉字数 < 6 ⇒ 报。
    for _i, m in enumerate(imgs):
        before = body[: m.start()].rstrip()
        before_line = before.split("\n")[-1].strip() if before else ""
        name = m.group(1).split("/")[-1]
        if len(CJK.findall(before_line)) < 6 and not before_line.startswith("|"):
            warns.append(f"[图无引出] {name} 前面没有一句正文承接")
        # 解读句的**窗口**：本图结尾 → 下一个 ## 标题 或 下一张图（取较近者）
        _seg_end = imgs[_i + 1].start() if _i + 1 < len(imgs) else len(body)
        _nxt_h2 = re.search(r"^##\s+", body[m.end(): _seg_end], re.M)
        if _nxt_h2:
            _seg_end = m.end() + _nxt_h2.start()
        _win = body[m.end(): _seg_end]
        if len(CJK.findall(_win)) < 6:
            warns.append(f"[图无解读] {name} 后面到下一节之间没有一句正文解读")

    # ---- E. 句子长度（可读性） ----
    ss = sentences(body)
    if ss:
        lens = [len(CJK.findall(s)) for s in ss]
        avg = sum(lens) / len(lens)
        mx = max(lens)
        if avg > MAX_SENT_AVG:
            warns.append(f"[句子偏长] 平均 {avg:.0f} 汉字（上限 {MAX_SENT_AVG}）")
        if mx > MAX_SENT_CJK:
            long_one = ss[lens.index(mx)]
            warns.append(f"[超长句] {mx} 汉字：「{long_one[:40]}…」")

    # ---- F. 具体性（反空泛） ----
    # 阿拉伯数字与中文数字都算 —— 只认阿拉伯数字会漏掉「三台机器」「两个副本」这类写法
    nums = re.findall(
        r"(?:\d+(?:\.\d+)?|[一二三四五六七八九十百千万几两]+)\s*"
        r"(?:%|MB|GB|KB|TB|ms|秒|分钟|小时|天|台|个|条|次|份|遍|轮|万|亿|倍|行|字节|票|台机器)",
        body,
    )
    if len(nums) / per_k < MIN_NUM_PER_K:
        warns.append(
            f"[不够具体] 具体数字 {len(nums)} 个 / {per_k:.1f}k 字"
            f"（下限 {MIN_NUM_PER_K}/千字）—— 多给数字、少下形容词"
        )
    pool = systems if systems is not None else DEFAULT_SYSTEMS
    named = sum(1 for s in pool if s.lower() in body.lower())
    if named < named_min:
        # ★ 报错信息要说清「它数的到底是什么」（2026-09-29 修，附录五十四）
        #   一位作者补了七个**真实芯片名**（POWER6/Denver/ROCK/…）而计数仍是 2 ——
        #   因为判据数的是「命中 course.toml 的 named_systems 池几个」，
        #   不是「点了多少专有名词」。⇒ 把池子写进报错里，作者就不必去读源码。
        # ★ 打印**本课**的池子（`extra`），而不是那份默认池（2026-09-29 修）
        #   起因：我上一版只打印 DEFAULT_SYSTEMS，而那是 cs168 的池子
        #   ⇒ 对另外四门课的作者，那条提示**指向错误的池子**（比不说更糟）。
        _extra_show = "/".join(str(x) for x in (extra or [])[:16])
        _pool_show = _extra_show if extra else "/".join(str(x) for x in DEFAULT_SYSTEMS[:14])
        warns.append(
            f"[点名不足] 只点到 {named} 个具体对象（建议 ≥{named_min}）"
            f" —— ★ 它数的是命中**池**里几个，不是「点了多少专有名词」；"
            f"补真实但不在池里的名字（如 POWER6/Denver）**一个都不算**。"
            f"池内前若干个：{_pool_show} …"
            f"（完整池见 course.toml 的 named_systems；修法是自然地提到池内成员）"
        )

    # ---- G. 结构与术语 ----
    if len(h2s) < MIN_H2:
        warns.append(f"[结构] 只有 {len(h2s)} 个二级小节（建议 ≥{MIN_H2}）")
    terms = len(re.findall(r"\[\[term:[^\]]+\]\]", body))
    if terms < MIN_TERMS:
        warns.append(f"[术语] 只标了 {terms} 个 [[term:]]（建议 ≥{MIN_TERMS}）")

    return errs, warns



# ---------------- 版面多样性（语料级）----------------
_RECT = re.compile(r"<rect\b([^>]*)/?>")
_ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')
_VIEWBOX = re.compile(r'viewBox="([\d.\s-]+)"')


def layout_fingerprint(svg: Path) -> str:
    """版面指纹 = 图内方块的 (x,y,w,h)，舍入到 10px 后排序。

    先排除画布矩形（覆盖整个 viewBox 的那块），否则所有同尺寸画布的图
    都会被判成「同一版面」—— 这是个很容易踩的坑（我们自己踩过一次）。
    """
    try:
        t = svg.read_text(encoding="utf-8")
    except OSError:
        return ""
    m = _VIEWBOX.search(t)
    vw, vh = (0.0, 0.0)
    if m:
        parts = m.group(1).split()
        if len(parts) >= 4:
            vw, vh = float(parts[2]), float(parts[3])
    boxes = []
    for mm in _RECT.finditer(t):
        a = dict(_ATTR.findall(mm.group(1)))
        if "width" not in a or "height" not in a:
            continue
        try:
            x, y = float(a.get("x", 0)), float(a.get("y", 0))
            w, h = float(a["width"]), float(a["height"])
        except ValueError:
            continue
        if vw and vh and w >= vw - 2 and h >= vh - 2:
            continue  # 画布
        boxes.append((round(x / 10), round(y / 10), round(w / 10), round(h / 10)))
    return ";".join(f"{a},{b},{c},{d}" for a, b, c, d in sorted(boxes))


def audit_layouts(root: Path) -> tuple[list[str], list[str]]:
    """检查整套图有没有「同一个模板只换文字」。"""
    figs = sorted((root / "content").rglob("figures/*.svg"))
    if len(figs) < 8:
        return [], []
    groups: dict[str, list[str]] = {}
    for f in figs:
        fp = layout_fingerprint(f)
        if fp:
            groups.setdefault(fp, []).append(f.name)
    if not groups:
        return [], []
    worst = max(groups.values(), key=len)
    ratio = len(worst) / len(figs)
    msg = (
        f"[版面复用] {len(worst)}/{len(figs)} 张图（{ratio:.0%}）的版面完全一致"
        f"（同为 {worst[0].split('.')[0]} 那类布局），只有文字不同。"
        f"例：{', '.join(sorted(worst)[:5])} …"
        "\n       版面应当与内容匹配：流程用链、对比用双列、状态用环、层次用树。"
        "\n       读者连着看到同一个形状几十次，视觉通道就失效了。"
    )
    if ratio > LAYOUT_HARD:
        return [msg], []
    if ratio > MAX_SAME_LAYOUT:
        return [], [msg]
    return [], []


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    ap = argparse.ArgumentParser(description="内容结构与密度审计")
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true", help="WARN 也算失败")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    files = sorted((root / "content").rglob("index.md"))
    if not files:
        print("内容审计：content/ 下没有 index.md —— 跳过")
        return 0

    print(f"内容审计：{len(files)} 篇")
    corpus_errs, corpus_warns = audit_layouts(root)
    n_err = n_warn = 0
    pool, named_min = systems_for(root)
    for f in files:
        errs, warns = audit(f, root, pool, named_min)
        rel = f.relative_to(root).as_posix()
        n_err += len(errs)
        n_warn += len(warns)
        if errs:
            print(f"\n  ❌ {rel}")
            for e in errs:
                print(f"       {e}")
            for w in warns:
                print(f"       ⚠️  {w}")
        elif warns:
            print(f"\n  ⚠️  {rel}")
            for w in warns:
                print(f"       {w}")
        else:
            print(f"  ✅ {rel}")

    for e in corpus_errs:
        print(f"\n  ❌ {e}")
        n_err += 1
    for w in corpus_warns:
        print(f"\n  ⚠️  {w}")
        n_warn += 1

    print()
    print(f"ERROR {n_err} 个，WARN {n_warn} 个")
    if n_err or (args.strict and n_warn):
        print("❌ 内容审计未通过。标准见 docs/figure-audit.md 与 docs/quality-audit.md")
        return 1
    print("✅ 内容审计通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
