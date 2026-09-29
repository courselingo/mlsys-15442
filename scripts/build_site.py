#!/usr/bin/env python3
"""把课程仓库的内容渲染成 MkDocs Material 站点。

设计要点：
  * **内容格式不变** —— `content/<NN>-<slug>/index.md` 与 `content/papers/<key>/index.md`
    仍是唯一的真相，本脚本只是把它们转成 MkDocs 认的 docs/。
  * **先过授权闸门** —— 直接调用 validate.py；闸门不过（退出码 1/3）就不构建。
  * `[[term:key]]` 在转换期变成 <abbr class="term">，读者悬停可见中英对照。
  * 若存在 `bilingual/<slug>.zh.md` 与 `.en.md`，该页自动获得逐段双语对照。

用法：python scripts/build_site.py [--root .] [--out site-mkdocs]
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import quote

import banners  # 同目录：页面顶部授权提示条
import llms  # 同目录：发布 llms.txt 与每页 Markdown

def licence_sentence(lic: dict) -> str:
    """由 course.toml 的 **[license] 表本身**推导首页授权横幅。

    ★ 绝不写死。许可写错是本项目最不该犯的错：同一句话对 A 级课程是事实，
      对 B 级课程就是虚假陈述。判定口径见 docs/content-policy.md。
    """
    lic = lic or {}
    terms = str(lic.get("terms", "")).strip() or "未声明"
    verified = bool(lic.get("verified", False))
    deriv = bool(lic.get("allows_derivatives", False))
    comm = bool(lic.get("allows_commercial", False))
    sa = bool(lic.get("share_alike", False))
    redist = str(lic.get("redistribution", "unknown")).lower()

    if not verified:
        # 没核实 = 不声称任何权利。只讲我们自己的原创内容。
        return (
            f"上游许可：**尚未核实**（{terms}）。\n\n"
            "因此本站**只发布 CourseLingo 自己撰写的原创讲解** —— 讲概念、不转载课程原文，"
            "也不做逐段对照。原作者与院校保留一切权利。\n\n"
        )

    parts = [f"上游许可：{terms}。"]
    if not deriv:
        parts.append("该许可**不允许衍生作品**，因此本站只发布原创讲解。")
    else:
        parts.append("允许翻译" + ("与商用" if comm else "，但**仅限非商用**") + "，需署名。")
        if sa:
            parts.append("**同协议（SA）**：本站由该材料衍生的内容同样以该协议发布。")
    if redist != "allowed":
        parts.append("我们**不转载**课程原始材料。")
    parts.append("原作者与院校保留其权利。")
    # 让每条一句，读起来是提示而不是律师函
    return "上游许可：" + "".join(x[len("上游许可："):] if x.startswith("上游许可：") else x for x in parts) + "\n\n"


def yq(s) -> str:
    """把任意字符串变成**合法的 YAML 双引号标量**。

    JSON 是 YAML 1.2 的子集，所以 json.dumps 的转义对 YAML 合法。
    只用标准库，不引入 PyYAML —— build_site.py 至今是零第三方依赖。

    ★ 为什么必须有它：课程标题来自上游，我们无权改（改了就是误写官方名称）。
    CS168 的官方标题逐字含 ": "，不加引号会让 mkdocs 直接解析失败。
    同类字符：`: ` ` #`、行首的 `* & ! | > % @ ` `。
    """
    import json
    return json.dumps(str(s), ensure_ascii=False)


TERM_RE = re.compile(r"\[\[term:([A-Za-z0-9_.\-]+)\]\]")
H1_RE = re.compile(r"^#\s+", re.M)

PLATFORM_DOCS = "https://github.com/courselingo/courselingo/blob/main/docs"


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def slugify(en: str) -> str:
    s = re.sub(r"[\s_]+", "-", en.strip().lower())
    s = re.sub(r"[^a-z0-9.\-]", "", s)
    return re.sub(r"-{2,}", "-", s).strip("-")


def split_front_matter(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "+++":
        return "", text
    for i in range(1, len(lines)):
        if lines[i].strip() == "+++":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return "", text


def strip_markers_for_scan(body: str) -> str:
    return TERM_RE.sub("", body)


def render_terms(body: str, terms: dict[str, tuple[str, str]]) -> str:
    """[[term:key]] -> <abbr>；每篇首次出现显示「中文（English）」。"""
    used: dict[str, int] = {}

    def repl(m: re.Match) -> str:
        key = m.group(1).lower()
        entry = terms.get(key)
        if not entry:
            return m.group(0)
        en, zh = entry
        used[key] = used.get(key, 0) + 1
        label = f"{zh}（{en}）" if used[key] == 1 else zh
        title = html.escape(f"{zh} · {en}", quote=True)
        return f'<abbr class="term" title="{title}">{label}</abbr>'

    return TERM_RE.sub(repl, body)


def run_validate(root: Path) -> int:
    """先过授权闸门。返回退出码。"""
    validator = root / "scripts" / "validate.py"
    proc = subprocess.run(
        [sys.executable, str(validator), "--root", str(root), "--quiet"],
        capture_output=True, text=True, encoding="utf-8",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        print(out, file=sys.stderr)
        label = "政策性拒绝（授权不允许传播）" if proc.returncode == 3 else "校验未通过"
        print(f"⛔ 站点构建中止：{label}（退出码 {proc.returncode}）", file=sys.stderr)
    return proc.returncode


def copy_figures(src_dir: Path, dst_dir: Path, seen: dict[str, str]) -> None:
    """把配图**平铺**复制到 docs/<section>/figures/。

    为什么平铺：MkDocs 的链接检查按"源文件所在目录"解析相对路径，浏览器按
    "页面 URL"解析；只有当 use_directory_urls=false 且图平铺时，两者才一致。
    同名即报错 —— 同一 section 平铺存放，静默覆盖会让某页悄悄显示别人的图。
    """
    if not src_dir.is_dir():
        return
    dst_dir.mkdir(parents=True, exist_ok=True)
    for f in sorted(src_dir.glob("*.svg")):
        owner = seen.get(f.name)
        if owner is not None and owner != str(src_dir):
            raise SystemExit(
                f"⛔ 配图文件名冲突：{f.name}\n"
                f"   同时出现在：{owner}\n"
                f"   以及：      {src_dir}\n"
                "   同一 section 的配图是平铺存放的，请改成唯一文件名（建议带页面前缀）。"
            )
        seen[f.name] = str(src_dir)
        shutil.copy2(f, dst_dir / f.name)


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    ap = argparse.ArgumentParser(description="渲染 MkDocs Material 站点")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="site-mkdocs")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "course.toml").exists():
        print(f"错误：{root} 下没有 course.toml", file=sys.stderr)
        return 2

    print("① 授权闸门")
    rc = run_validate(root)
    if rc != 0:
        return rc
    print("   ✅ 校验通过")

    cfg = tomllib.loads((root / "course.toml").read_text(encoding="utf-8"))
    course = cfg.get("course", {})
    site_title = course.get("title_zh") or course.get("title") or "CourseLingo"

    terms: dict[str, tuple[str, str]] = {}
    for t in tomllib.loads((root / "glossary.toml").read_text(encoding="utf-8"))["term"]:
        en, zh = str(t["en"]).strip(), str(t["zh"]).strip()
        if en and zh:
            terms[slugify(str(t.get("key") or en))] = (en, zh)

    papers: dict[str, dict] = {}
    pj = root / "papers.toml"
    if pj.exists():
        for p in tomllib.loads(pj.read_text(encoding="utf-8")).get("paper", []):
            papers[str(p.get("key", ""))] = p

    web = root / "websrc"
    docs = web / "docs"
    if docs.exists():
        shutil.rmtree(docs)
    (docs / "lectures").mkdir(parents=True)
    (docs / "papers").mkdir(parents=True)
    (docs / "assets").mkdir(parents=True)

    shutil.copy2(web / "assets" / "bi.css", docs / "assets" / "bi.css")
    shutil.copy2(web / "assets" / "bi.js", docs / "assets" / "bi.js")
    shutil.copy2(web / "assets" / "site.css", docs / "assets" / "site.css")
    shutil.copy2(web / "assets" / "mathjax.js", docs / "assets" / "mathjax.js")
    # 只复制 favicon。
    # logo.png / logo-square.png 曾经给 header 用，现在 header 用 Material 默认图标
    # （与 csdiy 一致），站内 0 处引用 —— 不再复制，省掉每站约 490 KB 的死重。
    for brand in ("favicon.png", "favicon-32.png"):
        src = root / "assets" / brand
        if src.is_file():
            shutil.copy2(src, docs / "assets" / brand)

    # ---------- 讲座 ----------
    seen_figs: dict[str, str] = {}
    lectures = []
    for p in sorted((root / "content").glob("*/index.md")):
        if "papers" in p.relative_to(root / "content").parts:
            continue
        fm_txt, body = split_front_matter(p.read_text(encoding="utf-8"))
        fm = tomllib.loads(fm_txt) if fm_txt else {}
        slug = str(fm.get("slug", p.parent.name))
        out = docs / "lectures" / f"{slug}.md"
        banner = banners.course_banner(cfg.get("license", {}) or {})
        out.write_text(
            (banner + "\n" if banner else "") + render_terms(body, terms),
            encoding="utf-8",
        )
        lectures.append((int(fm.get("lecture", 0)), str(fm.get("title", slug)), slug))
        copy_figures(p.parent / "figures", docs / "lectures" / "figures", seen_figs)

    lectures.sort()

    # ---------- 论文 ----------
    paper_pages = []
    for p in sorted((root / "content" / "papers").glob("*/index.md")):
        fm_txt, body = split_front_matter(p.read_text(encoding="utf-8"))
        fm = tomllib.loads(fm_txt) if fm_txt else {}
        key = str(fm.get("paper", p.parent.name))
        pbanner = banners.paper_banner((papers.get(key) or {}).get("license"))
        (docs / "papers" / f"{key}.md").write_text(
            (pbanner + "\n" if pbanner else "") + render_terms(body, terms),
            encoding="utf-8",
        )
        copy_figures(p.parent / "figures", docs / "papers" / "figures", seen_figs)
        paper_pages.append((key, str(fm.get("title", key))))
    paper_pages.sort()

    # ---------- 双语文件（留在仓库里，不进 docs/，避免被当成页面构建）----------
    bilingual_dir = root / "bilingual"
    bi_pairs: set[str] = set()
    if bilingual_dir.is_dir():
        for zh in sorted(bilingual_dir.glob("*.zh.md")):
            slug = zh.name[: -len(".zh.md")]
            if (bilingual_dir / f"{slug}.en.md").exists():
                bi_pairs.add(slug)

    # 双语对照要**转载原文**，与逐字稿同属「转载课程原始材料」，
    # 因此共用同一道闸门：只有 [license.materials].<kind> 明确为 true 才注入。
    mats = (cfg.get("license", {}) or {}).get("materials") or {}
    bilingual_ok = mats.get("notes") is True
    if bi_pairs and not bilingual_ok:
        print(
            "   [!] 有双语对照源文件，但 [license.materials].notes 未确认为 true ——\n"
            "       双语对照需要转载原文，故**不予注入**。已跳过："
            + ", ".join(sorted(bi_pairs))
        )

    # 给有双语配对且**授权允许**的讲座页追加指令
    for _, _, slug in lectures:
        if slug in bi_pairs and bilingual_ok:
            f = docs / "lectures" / f"{slug}.md"
            f.write_text(
                f.read_text(encoding="utf-8")
                + (
                    "\n\n## 逐段双语对照\n\n"
                    "左侧为中文，右侧为原文；可用上方按钮切换「对照 / 仅中文 / English」。\n\n"
                    f":::bilingual zh=bilingual/{slug}.zh.md en=bilingual/{slug}.en.md\n:::\n"
                ),
                encoding="utf-8",
            )

    # ---------- 术语表 ----------
    rows = "\n".join(
        f"| `{html.escape(en)}` | {html.escape(zh)} |" for en, zh in sorted(terms.values())
    )
    (docs / "glossary.md").write_text(
        f"# 术语表\n\n全课程统一译法：同一个概念在任何一讲里都用同一个词。共 **{len(terms)}** 条。\n\n"
        f"| English | 中文 |\n| --- | --- |\n{rows}\n",
        encoding="utf-8",
    )

    # ---------- 首页 ----------
    lec_list = "\n".join(
        f"- [{title}](lectures/{slug}.md)" for _, title, slug in lectures
    ) or "- （暂无）"
    pap_list = "\n".join(f"- [{title}](papers/{key}.md)" for key, title in paper_pages) or "- （暂无）"
    home_banner = banners.course_banner(cfg.get("license", {}) or {})
    (docs / "index.md").write_text(
        (home_banner + "\n\n" if home_banner else "")
        + f"# {site_title}\n\n"
        f"> **{course.get('title', '')}** · {course.get('institution', '')} "
        f"{course.get('course_number', '')}  \n"
        f"> 原课程：<{course.get('homepage', '')}>\n\n"
        "本站内容由 CourseLingo 用中文**重新讲解**，不是原文翻译，也非官方材料。\n\n"
        f"## 讲座\n\n{lec_list}\n\n## 经典论文\n\n{pap_list}\n\n"
        f"## 术语表\n\n[全部术语](glossary.md)\n\n"
        f"## 授权\n\n"
        + licence_sentence(cfg.get("license", {}) or {})
        + "\n"
        f"详细规则见[内容策略]({PLATFORM_DOCS}/content-policy.md)与"
        f"[论文授权]({PLATFORM_DOCS}/paper-licensing.md)。\n",
        encoding="utf-8",
    )

    # ---------- mkdocs.yml ----------
    nav = ["- 首页: index.md"]
    nav.append("- 讲座:")
    for n, title, slug in lectures:
        nav.append(f"    - {yq(f'第 {n} 讲 · {title}')}: lectures/{slug}.md")
    if paper_pages:
        nav.append("- 论文导读:")
        for key, title in paper_pages:
            nav.append(f"    - {yq(title)}: papers/{key}.md")
    nav.append("- 术语表: glossary.md")

    # 站点身份取自 course.toml 的 [site]（复制模板后必须改那里），
    # 不再硬编码 —— 否则新课程的右上角会指向 6.824 的仓库。
    site_cfg = cfg.get("site", {})
    repo_full = str(site_cfg.get("repo", "")).strip() or "courselingo/courselingo"
    site_url = str(site_cfg.get("url", "")).strip()

    cfg_yml = f"""site_name: {yq(site_title)}
# 右上角显示本课程的仓库。repo_name 会显示在图标旁（宽屏）。
# 带上组织名，让 CourseLingo 的归属一眼可见。
repo_url: {yq("https://github.com/" + repo_full)}
repo_name: {yq(repo_full)}
# 站点规范地址：项目站点必须带 /<repo>/ 前缀，否则 canonical 与 sitemap 会错，
# MkDocs 也会给出「site_url 未设置」的提示。
site_url: {yq(site_url or f"https://courselingo.github.io/{repo_full.split(chr(47))[-1]}/")}
# 本站的 docs/ 是 build_site.py **生成**的，不是源文件 ——
# 默认的「编辑此页」会指向生成物，所以关掉，避免误导贡献者。
edit_uri: ""
site_description: {yq(f"{course.get('title', '')} — CourseLingo 中文讲解")}
docs_dir: {docs.as_posix()}
site_dir: {(root / args.out).as_posix()}
use_directory_urls: false

theme:
  name: material
  language: zh
  # 左上角保持 Material 默认图标（不设 theme.logo）—— 与 csdiy 一致。
  # 课程归属信息放到右上角的仓库链接里，见下面的 repo_url / repo_name。
  favicon: assets/favicon.png
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.top
    - navigation.indexes
    - toc.follow
    - search.suggest
    - search.highlight
    - content.code.copy
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-night
        name: 切换到深色
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-sunny
        name: 切换到浅色
  icon:
    # 右上角仓库图标用 GitHub 品牌图标（csdiy 同款）
    repo: fontawesome/brands/github

extra_css:
  - assets/bi.css
  - assets/site.css
extra_javascript:
  - assets/bi.js
  - assets/mathjax.js
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js

markdown_extensions:
  - abbr
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - tables
  - toc:
      permalink: true
      toc_depth: 3
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - extensions.bilingual

extra:
  # 页脚图标链接（右上角是仓库；这里补充组织与平台仓库）
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/courselingo
      name: CourseLingo 组织
    - icon: fontawesome/solid/book
      link: https://courselingo.github.io/
      name: 组织主页
    - icon: fontawesome/solid/scale-balanced
      link: https://github.com/courselingo/courselingo/blob/main/docs/content-policy.md
      name: 内容与授权策略

nav:
{chr(10).join('  ' + line for line in nav)}
"""
    (web / "mkdocs.yml").write_text(cfg_yml, encoding="utf-8")

    # ---------- 构建 ----------
    print("② mkdocs build")
    env = {"PYTHONPATH": str(web), "PYTHONIOENCODING": "utf-8",
           "COURSELINGO_BASE_DIR": str(root)}
    import os
    proc = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "-f", str(web / "mkdocs.yml")],
        cwd=str(root), env={**os.environ, **env},
        capture_output=True, text=True, encoding="utf-8",
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    print(out[-2500:] if out else "(无输出)")
    if proc.returncode != 0:
        print(f"⛔ mkdocs 构建失败（退出码 {proc.returncode}）", file=sys.stderr)
        return 1

    # ---------- llms.txt + 每页 Markdown ----------
    print("③ llms.txt + 每页 Markdown")
    sections: dict[str, list[tuple[str, str]]] = {
        "开始": [("首页", "index")],
        "讲座": [(t, f"lectures/{s}") for _, t, s in lectures],
    }
    if paper_pages:
        sections["论文导读"] = [(t, f"papers/{k}") for k, t in paper_pages]
    sections["术语表"] = [("全部术语", "glossary")]
    n_pages, n_exp = llms.emit(
        root, docs, root / args.out, site_title,
        f"{course.get('title', '')} · {course.get('institution', '')} {course.get('course_number', '')} —— CourseLingo 中文讲解",
        sections,
        "本站内容由 CourseLingo 用中文**重新讲解**，不是原文翻译，也非官方材料。\n\n"
        "- 每页同时提供 HTML 与 Markdown（把 .html 换成 .md）\n"
        "- 术语表见 glossary.md；全课程同一概念同一译法\n"
        "- 上游许可与逐篇论文授权见 https://github.com/courselingo/courselingo/tree/main/docs\n",
    )
    print(f"   已发布 {n_pages} 个页面 Markdown，展开双语块 {n_exp} 处")

    html_files = sorted((root / args.out).rglob("*.html"))
    print(f"\n✅ 构建完成：{len(html_files)} 个 HTML")
    print(f"   入口：{root / args.out / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
