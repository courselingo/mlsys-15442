# CMU 15-442 / 15-642 · Machine Learning Systems

> CourseLingo 中文讲解 · 机器学习系统：从自动微分、CUDA 到 LLM 服务与内核优化

本仓库是 [CourseLingo](https://github.com/courselingo) 的一门课程站点。

## 授权

产出**不转载原文**，只发布 CourseLingo 自己的中文讲解与自绘配图。
原课程的授权与逐页核实记录见 `docs/audit/` 与平台仓库
[docs/full-translation-scope.md](https://github.com/courselingo/courselingo/blob/main/docs/full-translation-scope.md)。

站点：https://courselingo.github.io/mlsys-15442/

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `content/` | **唯一事实源**：讲座 Markdown + 自绘 SVG |
| `docs/audit/` | 授权核实、事实核对、配图复核、质量审计记录 |
| `scripts/` | 校验与构建脚本（零第三方依赖） |
| `websrc/` | 站点源（`mkdocs.yml` 由 `build_site.py` 生成） |

## 本地校验

```powershell
python scripts/validate.py --root .
python scripts/check_style.py --root .
python scripts/audit_content.py --root . --strict
python scripts/check_figures.py --root . --strict
python scripts/build_site.py --root . --out site-mkdocs
python scripts/check_reviewed.py --root .
```
