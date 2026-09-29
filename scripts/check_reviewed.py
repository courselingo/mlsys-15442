#!/usr/bin/env python3
"""把关 `status = "reviewed"`：**声称通过审核的页面，必须拿得出审核的证据。**

## 为什么需要这个脚本

`validate.py` 的 `VALID_STATUS = {"draft", "reviewed", "approved"}` ——
它**接受** `reviewed`，但**不为它检查任何东西**。也就是说：

    「reviewed」这个标签，此前完全靠人自觉。

而 `docs/quality-audit.md` §9 明确定义了它的前置条件：
    **P0/P1 清零 ＋ 有审核记录**

这两条**机器判不了**（P0/P1 是内容判断），所以不该由机检来判「内容是否合格」。
**但「有没有走完流程」是机器能判的**，而这个脚本判的就是后者：

  · 页面自称 `reviewed` ⇒ **必须**有一份对应它的审核记录；
  · 记录里**必须**写明透镜 3（陌生读者测试）的结论 —— 那是两道人工闸门之一；
  · 记录里**必须**同时钉住**内容哈希与工具哈希**（附录七）——
    否则「当时为什么绿」不可复现；
  · 该页的配图**不得**有未处理的「有错误 / 需小修」复核结论。

**它不判内容对不对，只判「你有没有把该做的做完并留下证据」。**
这是机检该做的部分；内容判断仍归两道人工闸门。

## 用法

    python check_reviewed.py --root <课程根目录> [--strict]

**draft 页：只提示，不报错**（它们本来就还没做完）。
**reviewed / approved 页：上述任一条不满足即 ERROR。**
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

CJK = re.compile(r"[\u4e00-\u9fff]")
H2 = re.compile(r"(?m)^##\s+(.+)$")


# ★★ 哈希必须**与行尾符无关** —— 否则「本地通过、CI 失败」是必然的。
#
# 实测（2026-09-28，mit-6.006 提级那次）：
#   工作区 peak-finding-1.svg = **CRLF** 47 处，SHA256 前16 = `7D016EFDD7E15438`
#   git HEAD 里的同一文件      = **LF**          SHA256 前16 = `4ADB2DF9FF520C8E`
#   全仓 86 个被跟踪文件里，**51 个的工作区字节 ≠ git 字节**（而 `git status` 干净，
#   因为 git 在比较时会做行尾归一化）。
#   于是 CI 的 `check_reviewed.py` 报「报告核的是旧版」—— **报告没错，文件也没错，
#   错的是「哈希」这个标识符：它把表示的差异当成了内容的差异。**
#
# ⇒ 凡计算用于**跨机器比对**的哈希，先做行尾归一化（CRLF → LF）。
#   这与 `附录七` 同源：标识符必须只随它该随的东西变。
def nhash(path: pathlib.Path) -> str:
    """行尾归一化后的 SHA256（大写十六进制）。CRLF 与 LF 得到同一个值。"""
    b = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest().upper()


def split_fm(text: str) -> dict[str, str]:
    if not text.startswith("+++"):
        return {}
    end = text.find("\n+++", 3)
    if end < 0:
        return {}
    fm: dict[str, str] = {}
    for ln in text[3:end].splitlines():
        m = re.match(r"\s*([A-Za-z_][\w-]*)\s*=\s*(.+?)\s*$", ln)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm


def find_audit(ad: pathlib.Path, page: pathlib.Path, content_root: pathlib.Path) -> list[pathlib.Path]:
    """找「这一页的」审核记录。

    ★ 匹配不能只看文件名。实测两个反例：
      · cs168 目录 01-internet-architecture-and-protocols，记录叫 lecture-01-quality-audit.md（按编号匹配）
      · mit-6.5840 GFS 目录 03-gfs，记录叫 mit-6.5840-03-gfs.md（按目录名匹配）
    另外**内容匹配要加门槛**：曾出现「给 02-rpc 找记录时，GFS 的记录因为交叉引用提到过 02-rpc 而被判 OK」——
    **「提到过这一页」不等于「是这一页的记录」**。门槛：出现在标题行，或至少出现 3 次。
    """
    if not ad.exists():
        return []
    stem = page.parent.name
    try:
        slug = page.parent.relative_to(content_root).as_posix()
    except ValueError:
        slug = stem
    num = re.match(r"(\d+)", stem)
    num = num.group(1) if num else ""
    # 论文页（content/papers/<name>/）用目录名匹配即可
    out = []
    for f in sorted(ad.glob("*.md")):
        fs = re.sub(r"[-_]", "", f.stem).lower()
        ss = re.sub(r"[-_]", "", stem).lower()
        if ss and ss in fs:
            out.append(f)
            continue
        if num and re.search(rf"(?<!\d)0*{num}(?!\d)", f.stem):
            out.append(f)
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        in_heading = any(slug in ln or stem in ln
                         for ln in t.splitlines() if ln.lstrip().startswith("#"))
        if in_heading or (t.count(slug) + t.count(stem)) >= 3:
            out.append(f)
    return out


def main(argv: list[str] | None = None) -> int:
    # ★ stdout 编码保护 —— 兄弟脚本都有，本脚本起初漏了。
    #
    # cs168-author 在 Windows 默认控制台（cp936 / Python 3.12）上实测：
    #   四条件全满足 + cp936  -> UnicodeEncodeError: 'gbk' codec can't encode '\u2705'
    #                            exit=1
    #   四条件全满足 + utf-8  -> ✅ 通过，exit=0
    # **也就是说：一个把所有 reviewed 条件都满足的页面，在 Windows 上仍然 exit 1。**
    #
    # 更坏的是它的**两种失效方向不对称**：
    #   · 有问题时：崩在 ❌ 那行，exit 恰好也是 1 —— 于是这个 bug **隐形**，
    #     只是把真正的原因吞掉（看到的是一个 UnicodeEncodeError，不是那几条问题）；
    #   · 没问题时：**致命的假阴性**，而且看起来像「内容不过」。
    # CI 跑在 Linux/UTF-8 上不受影响，所以它只会在人手动核 reviewing 时骗人。
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="把关 status=reviewed 的前置条件")
    ap.add_argument("--root", required=True)
    ap.add_argument("--strict", action="store_true", help="draft 页的提示也计入退出码")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    content = root / "content"
    ad = root / "docs" / "audit"
    if not ad.exists():
        ad = root.parent.parent / "courselingo" / "docs" / "audit"  # 平台仓兜底
    # ★ 配图复核报告的查找路径：**先看仓库内，再看工作区**。
    #
    # 本文件原先只指向 `root.parent.parent / "preview" / "visual-review"` ——
    # **那是工作区目录，不在课程仓库里。**
    # 结果：本地跑全绿、**CI 上必然失败**（实测：2026-09-28，cs168 提级那次
    # `Validate` 报「intro-1..8 无复核报告」，因为 CI 只 checkout 课程仓库）。
    #
    # ⇒ 这条错与整个项目的头号错误同类：**闸门要求的证据，住在被检查的东西之外。**
    #   修法不是让 CI 放宽，而是**让证据随产物一起走** ——
    #   复核报告是证据，必须与它判定的那个版本**同仓库、同提交**。
    #   （与 `附录九`「证据要落盘在下一个核对着会看的地方」同一条；
    #     而这里「下一个核对着」就是 CI。）
    vdirs = [root / "docs" / "audit" / "visual-review",
             root.parent.parent / "preview" / "visual-review"]
    vdir = next((d for d in vdirs if d.exists()), vdirs[0])

    # ★ 实测裁定表：允许「已实测证伪的复核结论」被显式覆盖。
    #   规则见 quality-audit.md 附录八 / 附录十一 / 附录十二，说明见本文件末尾。
    #
    # ★★ 裁定必须钉住**它所反驳的那份报告**（按内容哈希，不按时间）。
    #
    # 我先写的是「按 mtime 比较」：报告比裁定新 ⇒ 裁定不适用。
    # **本地测试通过，CI 上立刻失败** ——
    #   实测报错：`intro-6:裁定早于这份新报告（裁定 1790607479 < 报告 1790607479）`
    #   **两个时间戳印出来一模一样**，而分支却判成了「更新」。
    # 根因：**在干净检出里，git 把仓库里所有文件的 mtime 设成检出那一刻** ⇒
    #   **同一个仓库内比较 mtime 是没有任何意义的**（谁先谁后是任意的）。
    #
    # ⇒ 改成**内容哈希**：裁定表每行可写第 5 列「针对报告」，填那份报告 SHA256 的前 16 位。
    #   · 该列匹配当前报告 ⇒ 裁定生效（它反驳的正是这一份）；
    #   · 不匹配 / 该列空 ⇒ **不生效**，按新报告处置（旧的写法仍可用，只是不再覆盖）。
    # **这与 `附录五`、`附录七` 是同一条：结论绑「它被作出时的那个状态」，而状态的标识符是哈希，不是时间。**
    adj_path = ad / "visual-adjudications.md"
    adj: dict[str, tuple[str, str]] = {}   # 图 -> (依据, 针对的报告哈希前缀)
    if adj_path.exists():
        for ln in adj_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not ln.strip().startswith("|"):
                continue
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 4:
                continue
            fig, orig, verdict, basis = cells[0], cells[1], cells[2], cells[3]
            # 列序：| 图 | 原判定 | 裁定 | 依据 | 裁定人 | 针对报告 |
            # 只取十六进制字符 —— 单元格里常写成 `ABCD…`（反引号），直接比较会差一位。
            target = "".join(ch for ch in (cells[5] if len(cells) > 5 else "").upper()
                             if ch in "0123456789ABCDEF")
            if fig in ("图", "----", "---") or set(fig) <= set("-: "):
                continue
            # 只认「可用」，且依据必须**含数字**（= 有实测值，不是一句主观判断）
            if verdict == "可用" and re.search(r"\d", basis):
                adj[fig] = (basis, target)

    pages = sorted(content.rglob("index.md"))
    errs: list[str] = []
    notes: list[str] = []
    n_ok = 0

    for p in pages:
        text = p.read_text(encoding="utf-8")
        fm = split_fm(text)
        status = fm.get("status", "")
        rel = p.relative_to(content).as_posix()
        if status not in ("reviewed", "approved"):
            continue
        prob: list[str] = []
        recs = find_audit(ad, p, content)
        if not recs:
            prob.append("是 reviewed，但找不到对应的审核记录（§9 要求「有审核记录」）")
        else:
            lens = any(("透镜 3" in r.read_text(encoding="utf-8", errors="replace")
                        or "透镜三" in r.read_text(encoding="utf-8", errors="replace")
                        or "陌生读者" in r.read_text(encoding="utf-8", errors="replace"))
                       for r in recs)
            if not lens:
                prob.append("审核记录里没有透镜 3（陌生读者测试）的结论 —— 那是两道人工闸门之一")
            hashed = any(re.search(r"(?i)sha256|哈希", r.read_text(encoding="utf-8", errors="replace"))
                         for r in recs)
            if not hashed:
                prob.append("审核记录里没有 SHA256/哈希 —— 「当时为什么绿」将不可复现（附录七）")
        # 配图复核
        figs = sorted((p.parent / "figures").glob("*.svg"))
        bad = []
        unreadable = []
        for f in figs:
            rep = vdir / f"{root.name}__{f.stem}.md"
            if not rep.exists():
                # ★ 没有报告 ≠ 通过。缺证据就是缺证据。
                #   但「配图从没复核过」在 draft 阶段是常态，
                #   所以只在 reviewed 页上算问题（本函数只在 reviewed 页里跑）。
                unreadable.append(f"{f.stem}:无复核报告")
                continue
            t = rep.read_text(encoding="utf-8", errors="replace")
            # ★★ 先剥 Markdown 标记再匹配。
            #
            # 发现经过（2026-09-28，两个执行者先后报来同一件事）：
            #   ① cs168 的复核者指出：闸门是字面子串匹配，若报告写成 `**判定**：可用`
            #      （中间夹了 `**`），匹配不上 ⇒ 取到 "?" ⇒ `if v in ("有错误","需小修")`
            #      对 "?" 为假 ⇒ **静默放行，闸门就废了**。
            #   ② 随后实测：**我们自己的 `visual_review.py` 就在产出这种加粗体** ——
            #      它的 prompt 把判定写成反引号包裹的 `` `判定：可用` ``，
            #      模型于是回成 `**判定**：可用`。**管线产出的报告，管线自己读不出来。**
            #
            # ⇒ 判定必须**先规范化**：剥掉 `*` `_` `` ` `` 与空白。
            #   并保留失败关闭：**真的没有判定行**才算读不出（那才是缺证据）。
            flat = re.sub(r"[*_`\s]", "", t)
            v = next((x for x in ("有错误", "需小修", "可用") if f"判定：{x}" in flat), None)
            if v is None:
                # 给一条可操作的修法：告诉它要写成纯文本
                unreadable.append(
                    f"{f.stem}:读不出判定（报告里必须有 `判定：可用` / "
                    f"`判定：需小修` / `判定：有错误` 之一；加粗、反引号可接受，"
                    f"**完全没有判定行**不行）")
            elif v in ("有错误", "需小修"):
                bad.append(f"{f.stem}:{v}")
            elif v == "可用":
                # ★★ 「可用」也必须**对这一版**才作数。
                #
                # 报告里写着 `复核对象 SHA256(前16)：XXXX`。若当前 SVG 的哈希与它不符，
                # 说明**图在复核之后被改过** —— 那条「可用」是对旧版说的，不算数。
                #
                # 为什么要有这一步，而不是靠「刷新时别改图」这种纪律：
                # **我在同一天里两次让刷新与作者的编辑赛跑**（6.006 一次、cs168 一次），
                # 两次都是「我这边在复核、作者那边在改」。纪律挡住我，代码才挡得住所有人。
                # 而 `附录五` 早已写明：**一次复核的结论只对它看过的那一版成立。**
                # 报告里既然已经有哈希，就没有理由不校它。
                # 取「SHA256」之后第一段 ≥16 位的十六进制。
                # **不能**写成 `SHA256[^0-9A-F]*([0-9A-F]{16,})` —— 报告的前缀是 `(前16)：`，
                # 而 `前16` 里的 `1` `6` **本身就是十六进制字符**，`[^0-9A-F]*` 在此停下，
                # 捕获组从 `16` 开始、只拿两位就断。**第一次就是这么写的，实测才看出来** ——
                # 「写的时候看起来对」与「跑出来对」是两件事。
                m = re.search(r"(?i)SHA256(?:.{0,24}?)([0-9A-F]{16,64})", t)
                if not m:
                    unreadable.append(f"{f.stem}:报告里没有 `复核对象 SHA256`，无法确认它核对的是哪一版")
                else:
                    recorded = m.group(1).upper()
                    h = nhash(f)
                    if not h.startswith(recorded[:16]) and not recorded.startswith(h[:16]):
                        bad.append(f"{f.stem}:可用（但报告核的是旧版：报告 {recorded[:16]} / 现值 {h[:16]}）")
        # ★★ 应用实测裁定 —— **但裁定只对它作出时已存在的报告有效。**
        #
        # 起因（2026-09-28，实测）：我裁定 `peak-finding-4` 的四条几何主张不成立（都真被证伪了），
        # 写进裁定表。随后新一轮复核对**同一张没改过的图**给出了**两条全新的、真实的**意见
        # （「第 1 轮说明在框内、2/3 轮在框外，版式不统一」「第 2 行框外文字贴框过近」）。
        # **而按「图名匹配就覆盖」的写法，那两条会被旧裁定一并压掉** —— 一个真的问题会被静默吞掉。
        #
        # 根因：**裁定是「对某一次判定的反驳」，不是「对这张图的永久结论」。**
        # 把它当成后者，就等于把「那次判定错了」扩写成「这张图以后都没问题」。
        #
        # ⇒ 判据：**裁定的生效范围 = 它明确钉住的那一份报告。**
        #   按**内容哈希**钉（不按时间 —— 见文件上方 attach 时的长注：干净检出里 mtime 全相同）。
        #   报告对不上 ⇒ 裁定不适用 ⇒ 那份新报告必须被单独处置（重新裁，或照它改）。
        #   **这与 `附录五`（一次复核的结论只对它所看的版本成立）是同一个形状，只是对象换成了裁定。**
        if adj:
            kept = []
            for item in bad:
                name = item.split(":")[0]
                rep = vdir / f"{root.name}__{name}.md"
                if name in adj:
                    basis, target = adj[name]
                    cur = (nhash(rep)
                           if rep.exists() else "")
                    if not target:
                        reason = f"{name}:裁定未钉住报告哈希（第 5 列「针对报告」为空）"
                        kept.append(reason)
                        print(f"      ! {reason} ⇒ 裁定不适用，按新报告处置")
                        continue
                    if not cur.startswith(target[:16]):
                        reason = (f"{name}:裁定针对的是另一份报告"
                                  f"（裁定钉 {target[:16]} / 现值 {cur[:16] or '无报告'}）")
                        kept.append(reason)
                        print(f"      ! {reason} ⇒ 裁定不适用，按新报告处置")
                        continue
                    print(f"      · {name}：复核结论被实测裁定覆盖（{basis[:40]}…）")
                    continue
                kept.append(item)
            bad = kept
        if bad:
            prob.append("配图有这样未处理的复核结论：" + ", ".join(bad[:8]))
        if unreadable:
            prob.append("配图复核证据不完整（**缺证据不等于通过**）：" + ", ".join(unreadable[:8]))

        if prob:
            errs.append(f"{rel} —— status={status}")
            for x in prob:
                errs.append(f"    · {x}")
        else:
            n_ok += 1
            print(f"  ✅ {rel}  reviewed 的前置条件齐备")

    print(f"\n审 reviewed/approved 页：{n_ok} 页齐备，{sum(1 for _ in errs if _.startswith('    · '))} 个问题")
    if errs:
        print("\n❌ 以下页面声称通过审核，但拿不出证据：")
        for e in errs:
            print("  " + e)
        return 1
    print("✅ 所有声称 reviewed 的页面都能拿出审核证据")
    return 0


if __name__ == "__main__":
    sys.exit(main())
