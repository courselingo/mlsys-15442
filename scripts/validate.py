#!/usr/bin/env python3
"""CourseLingo 课程内容校验器。

零依赖：仅用 Python 3.11+ 标准库（tomllib）。退出码约定见 docs/pipeline-spec.md：
    0 = 通过（可能含 WARN）
    1 = 校验失败（存在 ERROR）
    2 = 用法 / IO 错误
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

TERM_RE = re.compile(r"\[\[term:([A-Za-z0-9_.\-]+)\]\]")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
TABLE_RE = re.compile(r"^\s*\|")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]*)\)")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

REQUIRED_COURSE = ["id", "title", "title_zh", "institution", "source_language", "target_language"]
REQUIRED_LICENSE = [
    "verified", "terms", "evidence_url", "checked_at",
    "allows_commercial", "allows_derivatives", "share_alike",
]
REQUIRED_LECTURE = [
    "title", "lecture", "slug", "status", "source_kind", "source_url", "output_mode",
]
REQUIRED_PAPER_PAGE = ["title", "paper", "status", "output_mode"]
REQUIRED_PAPER_FIELDS = ["key", "title", "authors", "venue", "url"]
REQUIRED_PAPER_LICENSE = [
    "verified", "terms", "evidence_url", "checked_at",
    "allows_translation", "allows_commercial", "share_alike",
]
VALID_STATUS = {"draft", "reviewed", "approved"}
VALID_MODES = {"explanation", "transcript"}
VALID_PAPER_MODES = {"guide", "translation"}
VALID_SOURCE_KINDS = {"notes", "video", "textbook", "slides", "other"}
PAPERS_DIRNAME = "papers"
VALID_REDISTRIBUTION = {"allowed", "forbidden", "unknown"}

# 退出码 3 = 政策性拒绝（授权明确不允许传播）。
# 与 1（内容有错，可以修）区分开：3 表示「这件事我们不做」，改内容是没用的。
REFUSED = 3

# 疑似整段转载原文的判定阈值
VERBATIM_MIN_CHARS = 400
VERBATIM_ASCII_RATIO = 0.90
VERBATIM_MIN_SPACES = 40


def slugify(en: str) -> str:
    """把英文术语转成标记 key：'distributed system' -> 'distributed-system'。"""
    s = en.strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9.\-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")


def force_utf8() -> None:
    """Windows 控制台默认 GBK，输出中文与 ✅ 会崩。统一改成 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


class Report:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str]] = []

    def error(self, where: object, msg: str) -> None:
        self.items.append(("ERROR", str(where), msg))

    def warn(self, where: object, msg: str) -> None:
        self.items.append(("WARN", str(where), msg))

    @property
    def errors(self) -> list[tuple[str, str, str]]:
        return [i for i in self.items if i[0] == "ERROR"]

    @property
    def warns(self) -> list[tuple[str, str, str]]:
        return [i for i in self.items if i[0] == "WARN"]


def load_toml(path: Path, rep: Report) -> dict | None:
    if not path.exists():
        rep.error(path.name, "文件不存在")
        return None
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        rep.error(path.name, f"TOML 解析失败：{exc}")
        return None
    except OSError as exc:
        rep.error(path.name, f"读取失败：{exc}")
        return None


def split_front_matter(text: str) -> tuple[str | None, str]:
    """按 +++ 分隔 TOML front matter 与正文。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "+++":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "+++":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def iter_paragraphs(body: str):
    """产出正文中的段落文本，跳过代码块 / 标题 / 表格行。"""
    in_fence = False
    buf: list[str] = []
    for raw in body.splitlines():
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            if buf:
                yield "\n".join(buf)
                buf = []
            continue
        if in_fence:
            continue
        if not raw.strip() or HEADING_RE.match(raw) or TABLE_RE.match(raw):
            if buf:
                yield "\n".join(buf)
                buf = []
            continue
        buf.append(raw)
    if buf:
        yield "\n".join(buf)


def strip_html_comments(text: str) -> str:
    """去掉 <!-- --> 注释：那是作者备忘，不是正文，也不该触发术语校验。"""
    return HTML_COMMENT_RE.sub("", text)


def license_allows(cfg: dict, source_kind: str) -> bool:
    """授权闸门判定。

    优先看 [license.materials] 是否按材料类型逐项核实 —— 因为「笔记已授权」不等于
    「视频也已授权」。没有该段时退回 [license].verified 这个总开关。
    """
    lic = cfg.get("license")
    if not isinstance(lic, dict):
        return False
    materials = lic.get("materials")
    if isinstance(materials, dict) and materials:
        return materials.get(source_kind) is True
    return lic.get("verified") is True


def ascii_ratio(s: str) -> float:
    if not s:
        return 0.0
    return sum(1 for c in s if ord(c) < 128) / len(s)


def verbatim_suspect(paragraph: str) -> str | None:
    """返回可疑文本；不像整段英文原文则返回 None。"""
    text = TERM_RE.sub("", paragraph)
    text = INLINE_CODE_RE.sub("", text)
    text = LINK_RE.sub(r"\1", text)
    text = re.sub(r"[*_>#]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= VERBATIM_MIN_CHARS:
        return None
    if ascii_ratio(text) < VERBATIM_ASCII_RATIO:
        return None
    # 单个超长 URL / 无空格串不算「散文」
    if text.count(" ") < VERBATIM_MIN_SPACES:
        return None
    return text


def check_course(cfg: dict, rep: Report) -> None:
    course = cfg.get("course")
    if not isinstance(course, dict):
        rep.error("course.toml", "缺少 [course] 段")
        return
    for key in REQUIRED_COURSE:
        if not str(course.get(key, "")).strip():
            rep.error("course.toml", f"[course].{key} 为必填且不能为空")

    license_ = cfg.get("license")
    if not isinstance(license_, dict):
        rep.error(
            "course.toml",
            "缺少 [license] 段（授权闸门）—— 授权未核实前，本课程只能产出 explanation 模式",
        )
        return
    for key in REQUIRED_LICENSE:
        if key not in license_:
            rep.error("course.toml", f"[license].{key} 为必填")
    if license_.get("verified") is True:
        if not str(license_.get("terms", "")).strip():
            rep.error("course.toml", "license.verified = true 但 terms 为空（必须写明许可条款）")
        if not str(license_.get("evidence_url", "")).strip():
            rep.error("course.toml", "license.verified = true 但 evidence_url 为空（必须可溯源）")
        if not str(license_.get("checked_at", "")).strip():
            rep.error("course.toml", "license.verified = true 但 checked_at 为空（须记录核实日期）")

    redistribution = license_.get("redistribution")
    if redistribution is not None and redistribution not in VALID_REDISTRIBUTION:
        rep.error(
            "course.toml",
            f"[license].redistribution={redistribution!r} 必须是 {sorted(VALID_REDISTRIBUTION)} 之一",
        )

    output = cfg.get("output")
    if not isinstance(output, dict) or output.get("default_mode") not in VALID_MODES:
        rep.error("course.toml", f"[output].default_mode 必须是 {sorted(VALID_MODES)} 之一")

    materials = license_.get("materials")
    if materials is not None:
        if not isinstance(materials, dict):
            rep.error("course.toml", "[license.materials] 必须是表（键为材料类型）")
        else:
            for k, v in materials.items():
                if k not in VALID_SOURCE_KINDS:
                    rep.error(
                        "course.toml",
                        f"[license.materials].{k} 不是合法材料类型（可选：{sorted(VALID_SOURCE_KINDS)}）",
                    )
                if not isinstance(v, bool):
                    rep.error("course.toml", f"[license.materials].{k} 必须是布尔值")


def check_glossary(gl: dict, rep: Report) -> dict[str, tuple[str, str]]:
    """校验术语表，返回 {key: (en, zh)}。"""
    terms = gl.get("term")
    if not isinstance(terms, list) or not terms:
        rep.error("glossary.toml", "至少需要一个 [[term]] 条目")
        return {}
    index: dict[str, tuple[str, str]] = {}
    for i, term in enumerate(terms, 1):
        if not isinstance(term, dict):
            rep.error("glossary.toml", f"第 {i} 个 [[term]] 不是表")
            continue
        en = str(term.get("en", "")).strip()
        zh = str(term.get("zh", "")).strip()
        if not en:
            rep.error("glossary.toml", f"第 {i} 个 [[term]] 缺少 en")
        if not zh:
            rep.error("glossary.toml", f"第 {i} 个 [[term]]（en={en!r}）缺少 zh")
        if not en or not zh:
            continue
        key = slugify(str(term.get("key") or en))
        if not key:
            rep.error("glossary.toml", f"术语 en={en!r} 无法生成合法 key")
            continue
        if key in index:
            rep.error(
                "glossary.toml",
                f"重复术语 key={key!r}（en={en!r} 与已有 {index[key][0]!r} 冲突）",
            )
            continue
        index[key] = (en, zh)
    return index


def check_body(rel: str, body: str, rep: Report, glossary_index: dict[str, tuple[str, str]]) -> None:
    """正文层面的检查：术语标记引用 + 原文转载探测 + 术语漂移。讲座与论文页共用。"""
    # 术语标记引用（行内 code 里的 [[term:key]] 是写法示例，不算引用）
    stripped = INLINE_CODE_RE.sub("", body)
    used: set[str] = set()
    for m in TERM_RE.finditer(stripped):
        key = m.group(1).lower()
        if key not in glossary_index:
            rep.error(rel, f"[[term:{key}]] 未在 glossary.toml 中定义")
        used.add(key)

    # ★ 闸门缺口（由 cs168-author 发现、Lead 复现后补上）：
    #   TERM_RE 的键只允许 [A-Za-z0-9_.-]，所以 [[term:physical layer]]（含空格）
    #   **不被识别为标记** —— 于是上面那个循环看不见它：不会报「未定义」，
    #   validate 干净通过，**而页面上会原样渲染出 [[term:physical layer]] 这段字面量**。
    #   这是「能骗过机检、却让成品出错」的一类写法，必须显式拦：
    #   凡出现 [[term: 字样，就必须整体匹配上合法标记。
    for m in re.finditer(r"\[\[term:([^\]]*)\]\]", stripped):
        if not re.fullmatch(r"[A-Za-z0-9_.\-]+", m.group(1)):
            rep.error(
                rel,
                f"术语标记 [[term:{m.group(1)}]] 的键含非法字符（只允许 A-Za-z0-9_.-）"
                f"⇒ 它不会被识别为标记，页面上会**原样显示这段字符**。"
                f"键请写成 [[term:{slugify(m.group(1))}]]",
            )

    # 原文转载探测 + 术语漂移
    for para in iter_paragraphs(body):
        suspect = verbatim_suspect(para)
        if suspect:
            rep.error(
                rel,
                "疑似整段转载英文原文（违反内容策略）："
                f"{suspect[:60]}…（{len(suspect)} 字符，几乎全为 ASCII）",
            )
        # 术语漂移：正文里出现了 glossary 的英文原词却没打标记。
        # ★ 必须先把 [[term:...]] 标记自身剥掉再找 —— 否则当 glossary 里有 en = "term"
        #   （Raft 的「任期」）这种词时，每个标记里的字面 "term" 都会误报；
        #   同理 en = "log" 会命中 [[term:write-ahead-log]] 的 key 文本。
        low = TERM_RE.sub(" ", para).lower()
        for key, (en, _zh) in glossary_index.items():
            if key in used:
                continue
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(en.lower())}(?![A-Za-z0-9])", low):
                rep.warn(
                    rel,
                    f"术语 {en!r} 在正文出现但未加 [[term:{key}]] 标记（可能术语漂移）",
                )


def check_paper_registry(cfg: dict, rep: Report) -> dict[str, dict]:
    """校验 papers.toml，返回 {key: paper}。"""
    papers = cfg.get("paper")
    if papers is None:
        return {}
    if not isinstance(papers, list):
        rep.error("papers.toml", "[[paper]] 必须是数组表")
        return {}

    index: dict[str, dict] = {}
    for i, paper in enumerate(papers, 1):
        if not isinstance(paper, dict):
            rep.error("papers.toml", f"第 {i} 个 [[paper]] 不是表")
            continue
        key = str(paper.get("key", "")).strip()
        if not key:
            rep.error("papers.toml", f"第 {i} 个 [[paper]] 缺少 key")
            continue
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
            rep.error("papers.toml", f"key={key!r} 不合规（只要小写字母、数字与连字符）")
        if key in index:
            rep.error("papers.toml", f"重复的 paper key={key!r}")
            continue
        for field in REQUIRED_PAPER_FIELDS:
            if field == "key":
                continue
            if field == "authors":
                if not isinstance(paper.get("authors"), list) or not paper.get("authors"):
                    rep.error("papers.toml", f"{key}: authors 必须是非空数组")
            elif not str(paper.get(field, "")).strip():
                rep.error("papers.toml", f"{key}: 缺少 {field}")

        lic = paper.get("license")
        if not isinstance(lic, dict):
            rep.error("papers.toml", f"{key}: 缺少 [paper.license] 段")
        else:
            for field in REQUIRED_PAPER_LICENSE:
                if field not in lic:
                    rep.error("papers.toml", f"{key}: [paper.license].{field} 为必填")
            if lic.get("verified") is True:
                for field in ("terms", "evidence_url", "checked_at"):
                    if not str(lic.get(field, "")).strip():
                        rep.error(
                            "papers.toml",
                            f"{key}: license.verified = true 但 {field} 为空（必须可溯源）",
                        )
            r = lic.get("redistribution")
            if r is not None and r not in VALID_REDISTRIBUTION:
                rep.error(
                    "papers.toml",
                    f"{key}: [paper.license].redistribution={r!r} 必须是 {sorted(VALID_REDISTRIBUTION)} 之一",
                )
        index[key] = paper
    return index


def paper_allows_translation(paper: dict | None) -> bool:
    """论文全文翻译闸门。

    与逐字稿同级：翻译整篇论文是复制全部表达的衍生作品。
    必须「已核实」**且**条款明确允许翻译，缺一不可。
    """
    if not isinstance(paper, dict):
        return False
    lic = paper.get("license")
    if not isinstance(lic, dict):
        return False
    return lic.get("verified") is True and lic.get("allows_translation") is True


def course_refusal_reason(cfg: dict | None) -> str | None:
    """课程层面是否明确不允许传播。返回理由，或 None。"""
    lic = (cfg or {}).get("license")
    if not isinstance(lic, dict):
        return None
    if lic.get("redistribution") != "forbidden":
        return None
    evidence = str(lic.get("evidence_url", "")).strip()
    terms = str(lic.get("terms", "")).strip()
    detail = "；".join(x for x in (terms, evidence) if x)
    return "课程授权明确不允许传播（[license].redistribution = \"forbidden\"）" + (
        f" —— {detail}" if detail else ""
    )


def paper_refusal_reason(paper: dict, key: str) -> str | None:
    """论文层面是否明确不允许传播。"""
    lic = paper.get("license")
    if not isinstance(lic, dict):
        return None
    if lic.get("redistribution") != "forbidden":
        return None
    evidence = str(lic.get("evidence_url", "")).strip()
    return (
        f"论文 {key!r} 明确不允许传播（[paper.license].redistribution = \"forbidden\"）"
        + (f" —— {evidence}" if evidence else "")
    )


def print_refusal(reasons: list[str], where: str) -> None:
    """打印政策性拒绝。刻意写得毫不含糊 —— 这不是配置错误，是「我们不做」。"""
    print("", file=sys.stderr)
    print("⛔ 拒绝执行 —— CourseLingo 不为该课程产出或发布任何内容。", file=sys.stderr)
    print("", file=sys.stderr)
    for r in reasons:
        print(f"   理由：{r}", file=sys.stderr)
    print("", file=sys.stderr)
    print("   这是**政策性拒绝**，不是校验报错：改内容没有用。", file=sys.stderr)
    print("   本项目遵守「课程规定优先」：课程不允许传播，我们就不做。", file=sys.stderr)
    print(f"   若授权状况确已变化，请更新 {where} 的 redistribution 字段并附上依据。", file=sys.stderr)
    print("   见 docs/content-policy.md 与 LICENSE-CONTENT。", file=sys.stderr)
    print("", file=sys.stderr)


def check_paper_page(
    path: Path,
    rel: str,
    rep: Report,
    papers_index: dict[str, dict],
    glossary_index: dict[str, tuple[str, str]],
    seen_keys: dict[str, str],
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        rep.error(rel, f"读取失败：{exc}")
        return

    fm_text, body = split_front_matter(text)
    if fm_text is None:
        rep.error(rel, "缺少 +++ TOML front matter")
        return
    body = strip_html_comments(body)
    try:
        fm = tomllib.loads(fm_text)
    except tomllib.TOMLDecodeError as exc:
        rep.error(rel, f"front matter TOML 解析失败：{exc}")
        return

    if str(fm.get("kind", "")).strip() != "paper":
        rep.error(rel, '论文页必须写 kind = "paper"')
    for field in REQUIRED_PAPER_PAGE:
        if field not in fm:
            rep.error(rel, f"front matter 缺少必填字段 {field}")

    if fm.get("status") not in VALID_STATUS:
        rep.error(rel, f"status={fm.get('status')!r} 必须是 {sorted(VALID_STATUS)} 之一")

    key = str(fm.get("paper", "")).strip()
    if key:
        if key in seen_keys:
            rep.error(rel, f"paper={key!r} 与 {seen_keys[key]} 重复")
        else:
            seen_keys[key] = rel
        if key not in papers_index:
            rep.error(rel, f"paper={key!r} 未在 papers.toml 中登记")

    mode = fm.get("output_mode")
    if mode not in VALID_PAPER_MODES:
        rep.error(rel, f"output_mode={mode!r} 必须是 {sorted(VALID_PAPER_MODES)} 之一")
    elif mode == "translation" and not paper_allows_translation(papers_index.get(key)):
        lic = (papers_index.get(key) or {}).get("license") or {}
        rep.error(
            rel,
            f'⛔ 论文翻译闸门：output_mode="translation"，但论文 {key!r} 的授权不允许翻译'
            f"（verified={lic.get('verified')!r}, allows_translation={lic.get('allows_translation')!r}）。"
            "翻译整篇论文属于衍生作品，必须先逐篇核实。见 docs/paper-licensing.md",
        )

    if not str(fm.get("title", "")).strip():
        rep.error(rel, "title 不能为空")

    check_body(rel, body, rep, glossary_index)


def check_lecture(
    path: Path,
    rel: str,
    rep: Report,
    glossary_index: dict[str, tuple[str, str]],
    cfg: dict,
    papers_index: dict[str, dict],
    seen_lectures: dict[int, str],
    seen_slugs: dict[str, str],
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        rep.error(rel, f"读取失败：{exc}")
        return

    fm_text, body = split_front_matter(text)
    if fm_text is None:
        rep.error(rel, "缺少 +++ TOML front matter")
        return
    body = strip_html_comments(body)
    try:
        fm = tomllib.loads(fm_text)
    except tomllib.TOMLDecodeError as exc:
        rep.error(rel, f"front matter TOML 解析失败：{exc}")
        return

    for key in REQUIRED_LECTURE:
        if key not in fm:
            rep.error(rel, f"front matter 缺少必填字段 {key}")

    lecture_no = fm.get("lecture")
    if not isinstance(lecture_no, int):
        rep.error(rel, "lecture 必须是整数")
    elif lecture_no in seen_lectures:
        rep.error(rel, f"lecture={lecture_no} 与 {seen_lectures[lecture_no]} 重复")
    else:
        seen_lectures[lecture_no] = rel

    slug = str(fm.get("slug", "")).strip()
    if slug:
        if slug in seen_slugs:
            rep.error(rel, f"slug={slug!r} 与 {seen_slugs[slug]} 重复")
        else:
            seen_slugs[slug] = rel
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            rep.error(rel, f"slug={slug!r} 不合规（只允许小写字母、数字与连字符）")

    status = fm.get("status")
    if status not in VALID_STATUS:
        rep.error(rel, f"status={status!r} 必须是 {sorted(VALID_STATUS)} 之一")

    kind = fm.get("source_kind")
    if kind not in VALID_SOURCE_KINDS:
        rep.error(rel, f"source_kind={kind!r} 必须是 {sorted(VALID_SOURCE_KINDS)} 之一")

    if not str(fm.get("source_url", "")).strip():
        rep.error(rel, "source_url 不能为空（署名与可溯源要求）")

    mode = fm.get("output_mode")
    if mode not in VALID_MODES:
        rep.error(rel, f"output_mode={mode!r} 必须是 {sorted(VALID_MODES)} 之一")
    elif mode == "transcript" and not license_allows(cfg, str(kind)):
        rep.error(
            rel,
            f'⛔ 授权闸门：output_mode="transcript"，但 course.toml 未核实 {kind!r} 这类材料的授权'
            "（[license.materials] 逐项核实，或 [license].verified 总开关）。"
            "翻译完整逐字稿属于衍生作品，必须先核实该类材料的授权。见 docs/content-policy.md",
        )

    # 可选：本讲涉及哪些论文（须在 papers.toml 中登记）
    papers_ref = fm.get("papers")
    if papers_ref is not None:
        if not isinstance(papers_ref, list):
            rep.error(rel, "papers 必须是数组")
        else:
            for k in papers_ref:
                if str(k) not in papers_index:
                    rep.error(rel, f"papers 引用了未登记的论文 {str(k)!r}（见 papers.toml）")

    check_body(rel, body, rep, glossary_index)


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description="CourseLingo 课程内容校验器")
    parser.add_argument("--root", default=".", help="课程仓库根目录（默认当前目录）")
    parser.add_argument("--quiet", action="store_true", help="只输出问题与结论")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"错误：根目录不存在 {root}", file=sys.stderr)
        return 2

    rep = Report()
    cfg = load_toml(root / "course.toml", rep)
    gl = load_toml(root / "glossary.toml", rep)

    license_verified = False
    if cfg:
        check_course(cfg, rep)
        license_ = cfg.get("license") or {}
        license_verified = license_.get("verified") is True

    glossary_index: dict[str, tuple[str, str]] = {}
    if gl:
        glossary_index = check_glossary(gl, rep)

    papers_index: dict[str, dict] = {}
    if (root / "papers.toml").exists():
        papers_cfg = load_toml(root / "papers.toml", rep)
        if papers_cfg:
            papers_index = check_paper_registry(papers_cfg, rep)

    # ★ 政策性拒绝优先于一切校验：课程不允许传播，我们就不做。
    #   写在最前面，是为了让输出只有一条明确结论，而不是被一堆校验报错淹没。
    course_reason = course_refusal_reason(cfg)
    if course_reason:
        print_refusal([course_reason], "course.toml")
        return REFUSED

    content_dir = root / "content"
    lectures: list[Path] = []
    paper_pages: list[Path] = []
    if not content_dir.is_dir():
        rep.error("content/", "目录不存在")
    else:
        lectures = sorted(
            p for p in content_dir.glob("*/index.md")
            if PAPERS_DIRNAME not in p.relative_to(content_dir).parts
        )
        papers_dir = content_dir / PAPERS_DIRNAME
        paper_pages = sorted(papers_dir.glob("*/index.md")) if papers_dir.is_dir() else []

        if not lectures and not paper_pages:
            rep.error(
                "content/",
                "没有任何内容（讲座 content/<slug>/index.md 或论文 content/papers/<key>/index.md）",
            )

        # ★ 论文级政策性拒绝：只为**实际存在页面**的论文触发，
        #   不因为 papers.toml 里登记了一篇无关的「禁止传播」论文就全盘拒绝。
        paper_reasons = []
        for p in paper_pages:
            key = p.parent.name
            paper = papers_index.get(key)
            if paper:
                reason = paper_refusal_reason(paper, key)
                if reason:
                    paper_reasons.append(reason)
        if paper_reasons:
            print_refusal(paper_reasons, "papers.toml")
            return REFUSED

        seen_lectures: dict[int, str] = {}
        seen_slugs: dict[str, str] = {}
        for p in lectures:
            check_lecture(
                p, str(p.relative_to(root)).replace("\\", "/"),
                rep, glossary_index, cfg, papers_index, seen_lectures, seen_slugs,
            )

        seen_paper_keys: dict[str, str] = {}
        for p in paper_pages:
            check_paper_page(
                p, str(p.relative_to(root)).replace("\\", "/"),
                rep, papers_index, glossary_index, seen_paper_keys,
            )

    if not args.quiet:
        print(f"课程仓库：{root}")
        print(f"讲座 {len(lectures)} 篇   论文页 {len(paper_pages)} 篇   "
              f"术语 {len(glossary_index)} 条   论文登记 {len(papers_index)} 篇")
        print(f"授权状态：{'已核实' if license_verified else '未核实（仅允许 explanation 模式）'}")
        print("-" * 68)

    for level, where, msg in rep.items:
        icon = "❌" if level == "ERROR" else "⚠️ "
        print(f"{icon} [{where}] {msg}")

    print("-" * 68)
    # ★★ 术语键不得含空格（2026-09-29 加；起因见 quality-audit 附录四十八）
    #   glossary.toml 里曾有 9 个 `key = "含 空格"`，而 [[term:xxx]] 只接受 [A-Za-z0-9_.-]
    #   ⇒ 照抄 glossary 的键必然产生非法标记，而那种键**永远无法被引用**
    #   ⇒ 所以在这里直接拦掉：**让这类键写不出来**（附录二十六）。
    for _g in sorted(root.rglob("glossary.toml")):
        try:
            _txt = _g.read_text(encoding="utf-8")
        except Exception:
            continue
        for _m in re.finditer(r'^\s*key\s*=\s*"([^"]*)"', _txt, re.M):
            _k = _m.group(1)
            if _k and not re.fullmatch(r"[A-Za-z0-9_.\-]+", _k):
                rep.error(
                    "glossary.toml",
                    f"术语键非法：「{_k}」含 [[term:]] 无法表达的字符"
                    f"（只允许字母/数字/_ . -）—— 这种键**永远引用不了**，请改成连字符形式",
                )
    print(f"结果：{len(rep.errors)} 个错误，{len(rep.warns)} 个警告")

    if rep.errors:
        print("校验失败。授权与术语问题请勿绕过 —— 见 docs/content-policy.md")
        return 1
    print("校验通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
