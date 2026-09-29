# CI 工作流说明 · `.github/workflows/`

本目录随平台仓的 `template/` 一起复制进**每个课程仓**。每个课程仓独立部署、独立授权、独立下线 —— 这也是为什么 CI 放在课程仓而不是只放在平台仓。

三个工作流都是**零依赖**的：只用 `ubuntu-latest` 自带的 Python 3.12 标准库，不跑 `pip install`，不跑 `npm install`。

| 文件 | 触发 | 作用 |
| --- | --- | --- |
| `validate.yml` | 每次 push、每个 PR、手动触发 | 跑 `python scripts/validate.py`，有 ERROR 即失败（退出码非 0） |
| `deploy.yml` | push 到 `main`、手动触发 | `validate` → `build` → 部署 `site/` 到 GitHub Pages |
| `link-check.yml` | 每周一 02:00 UTC（北京时间 10:00）、手动触发 | 探测所有讲座的 `source_url`，失效则创建/更新 issue |

---

## 1. `validate.yml`

- **做什么**：`actions/checkout` → `actions/setup-python`(3.12) → `python scripts/validate.py`。
- **权限**：`contents: read`（只读仓库就够）。
- **密钥**：不需要。
- **失败意味着什么**：退出码 `1` = 有 ERROR（授权闸门被触发、术语引用不存在、front matter 缺字段、讲座号/slug 重复、正文出现大段疑似原文转载）；退出码 `2` = 用法或 IO 错误。任何一种都会让 PR 显示红叉。
- **并发**：同一分支的新提交会取消上一次仍在跑的校验。

## 2. `deploy.yml`

- **做什么**：三个 job 串联 —— `validate` → `build` → `deploy`。
  1. `validate` 跑 `scripts/validate.py`；
  2. `build` 用 `actions/configure-pages` 读出站点的 base path，跑 `python scripts/build.py --out site --base-url "<base_path>/"`，再用 `actions/upload-pages-artifact` 上传 `site/`；
  3. `deploy` 用 `actions/deploy-pages` 发布。
- **★ 授权闸门如何阻止部署**：`build` 依赖 `validate`，`deploy` 依赖 `build`（YAML 里的 `needs:`）。只要 `validate` 失败，GitHub 就不会运行后续 job，**站点不会更新**。例如某讲座写了 `output_mode = "transcript"`，而 `course.toml` 里 `license.verified != true`，`validate.py` 退出 1 → 部署在这一步就断了。这是机制保证，不是靠人记得。
- **权限**：`contents: read`、`pages: write`、`id-token: write`（后两个是 Pages 官方部署方式的硬要求，`id-token` 用于 OIDC）。
- **密钥**：不需要。全部用仓库自带的 `github.token`。
- **并发**：`group: pages`、`cancel-in-progress: false` —— 同一时刻只有一个部署在跑，且不打断进行中的部署（否则线上会留下半成品站点）。

## 3. `link-check.yml`

- **做什么**：读取 `content/**/index.md` 的 TOML front matter（`tomllib`），取出 `source_url`，并发探测（`urllib`，每个链接最多重试 3 次）。结果是：
  - `404` / `410`、域名失效、超时 → 判定 **fail**；
  - `403` / `429` → 判定 **warn**（很多站点反爬或限流，机器人拿不到 200 不代表链接坏了），只提示人工确认；
  - 有任何 **fail** 时，工作流退出 1，并由第二步**创建或更新**一个标题为 `[link-check] 失效的 source_url` 的 issue（已存在则改写正文，不让 issue 泛滥）。报告同时写入 `link-report.md` 并打印在日志里。
- **权限**：`contents: read`、`issues: write`（写 issue 必需）。
- **密钥**：不需要，用 `github.token`。若课程仓是组织内私有仓并关闭了 Actions 的默认 token 权限，需要在 Settings → Actions → General 里允许 workflow 的 `issues: write` 权限。
- **为什么内联 Python 而不新增脚本**：`scripts/` 下只有 `validate.py` 与 `build.py` 是规范定义的（见 `docs/pipeline-spec.md` §6/§7）。链接检查属于运维巡检，逻辑直接内联在工作流里，避免出现第三个"半官方"脚本。
- **注意**：定时工作流在仓库连续 60 天没有任何活动后会被 GitHub 自动停用；届时手动 `Run workflow` 一次或随便提交一次即可恢复。

---

## 4. 维护者一次性设置（仓库 Settings）

每个课程仓**第一次**要部署时，管理员做这几步：

1. **启用 Pages**：Settings → Pages → Build and deployment → **Source 选 "GitHub Actions"**（不要选 "Deploy from a branch"）。
   - 如果没启用，`actions/configure-pages` 会因为拿不到 Pages 站点信息而失败。这是唯一一个必须在网页上手动做的设置，`deploy.yml` 无法替你开。
2. **（可选）自定义域名**：Settings → Pages → Custom domain 填 `docs.example.com`，保存；随后到 DNS 服务商按提示加记录（子域名 → CNAME 到 `<owner>.github.io`；裸域 → A 记录指向 GitHub Pages 的 IP）。等 DNS 生效后勾上 **Enforce HTTPS**。
   - 用 GitHub Actions 发布时**不需要**在仓库里放 `CNAME` 文件：自定义域名存在 Pages 设置里，产物里的 `CNAME` 会被忽略（GitHub 官方文档原话）。所以本模板不生成该文件。
3. **（建议）分支保护**：Settings → Branches → 给 `main` 加规则，要求 `Validate / 内容校验` 这个检查通过后才能合并。这样"闸门"在合并前就生效，而不是等 push 到 `main` 才发现。
4. **（可选）首次运行**：Actions 页面允许 workflow 运行。组织仓第一次跑第三方 action 可能需要管理员批准。

## 5. 为什么 action 固定到 main 版本号（`@v7` / `@v6` / `@v5`）

- 固定**主版本标签**（`@v7`）而不是 `@main`：`main` 是开发分支，行为随时会变；主版本标签由官方在发版时移动，能自动拿到安全修复和补丁，同时不会跨大版本破坏接口。
- 也不固定到完整版本号（`@v5.0.0`）：会错过补丁，需要 Dependabot 频繁改文件。等仓库规模变大、需要可复现构建时再改用 commit SHA 锁定。
- **当前版本（2026-09-28 通过 `git ls-remote` 与 GitHub Releases API 核实）**：

  | Action | 本模板使用 | 最新主版本 | 最新具体版本 |
  | --- | --- | --- | --- |
  | `actions/checkout` | `@v7` | v7 | v7.0.1 |
  | `actions/configure-pages` | `@v6` | v6 | v6.0.0 |
  | `actions/upload-pages-artifact` | `@v5` | v5 | v5.0.0 |
  | `actions/deploy-pages` | `@v5` | v5 | v5.0.1 |
  | `actions/setup-python` | `@v7` | v7 | v7.0.0 |

- **`actions/setup-python` 已升到 `@v7`**：spec §8 原先冻结的是 `@v5`（内部 `node20`），实测当前最新主版本是 **v7**（`node24`）。升级前已核实 v7 的 `action.yml` **仍接受 `python-version` 输入**，因此三个 YAML 只改了版本号，没动任何配置。`docs/pipeline-spec.md` §8 已同步更新。

## 6. 本机/本地预检

CI 跑的就是你自己能在本地跑的两条命令，不需要任何安装：

```bash
python scripts/validate.py
python scripts/build.py --out site --base-url /
```

失败时先本地复现，比反复 push 试 CI 快得多。
