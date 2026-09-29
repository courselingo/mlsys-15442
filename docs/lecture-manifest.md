# 讲次清单 · CMU 15-442 / 15-642 Machine Learning Systems

> 本文件定义这门课的「**全量**」= 下表全部讲授单元。逐讲产出一页。
> 授权：**CC BY-NC 4.0**（仓库根 `LICENSE`，19,342 B）。第二人复核见
> 平台仓库 `docs/audit/licence-mlsys-15442-second-review.md`。
> 依据：`_sources/mlsys-15442/evidence/mlsys-site-lectures.yml`（站点源数据，权威排期）。

## 授权边界（写作时不变）

**可用**：课程自制讲义（`/slides/*.pdf` 与网页版讲义 `data_layout/`、`modern-gpu-gemm/`、`tirx-gemm/`）。
**不可用**：`slides/` 里混放的**三份第三方客座/业界演讲**
（`HaibinLinTalk`（ByteDance Seed）/ Tim Dettmers / Zihao Ye（UW & NVIDIA））；
**不在 `lectures.yml` 排期里的 PDF** ⇒ 视为第三方遗留文件。
**永久排除**：作业与考试题面/解答（3 个作业仓库 LICENSE 探针是 14 B 的 `404: Not Found` ⇒ 无许可；
`assignment-tirx-gemm` 虽是 Apache-2.0，但**仍属作业材料**，按学术诚信一并排除）。

## 讲次表（21 讲）

| # | slug（拟定） | 标题（原文） | slides |
| --- | --- | --- | --- |
| 1 | `why-ml-systems` | Week 1: Why ML Systems? | `/slides/01-course-introduction.pdf` |
| 2 | `introduction-to-mlsys` | Week 1: Introduction to Machine Learning Systems | `/slides/02-introduction-to-MLSys.pdf` |
| 3 | `deep-learning-abstraction` | Week 2: Intro to deep learning and programming abstraction | `/slides/03-deep-learning-programming-abstraction.pdf` |
| 4 | `automatic-differentiation` | Week 3: Automatic Differentiation | `/slides/04-automatic-differentiation.pdf` |
| 5 | `optimizing-linear-algebra` | Week 3: Optimizing Linear Algbera | `/slides/05-hardware-acceleration.pdf` |
| 6 | `cuda-programming-1` | Week 4: GPU Architecture and CUDA Programming (1) | `/slides/06-CUDA-programming.pdf` |
| 7 | `cuda-programming-2` | Week 4: GPU Architecture and CUDA Programming (2) | `/slides/06-CUDA-programming.pdf` |
| 8 | `transformer-attention` | Week 5: Case study: Transformer, Attention, Optimizations | `/slides/07-transformers-attention.pdf` |
| 9 | `ml-parallelization-1` | Week 5: ML Parallelization (Data Parallelism and Zero Redundancy) | `/slides/08-ML-parallelization-part1.pdf` |
| 10 | `ml-parallelization-2` | Week 6: ML Parallelization (Model and Pipeline Parallelism) | `/slides/09-ML-parallelization-part2.pdf` |
| 11 | `memory-optimization` | Week 6: Memory Optimizations: Tensor Rematerialization and Offload | `/slides/11-memory-optimization.pdf` |
| 12 | `ml-compiler-data-layout` | Week 7: ML Compiler - Data Layouts | `/slides/data_layout/`（网页版） |
| 13 | `ml-compiler-gemm` | Week 7: ML Compiler -- GEMM on Modern GPUs | `/slides/modern-gpu-gemm/`（网页版） |
| 14 | `llm-serving-1` | Week 9: LLM Serving (Continuous Batching, PagedAttention, RadixAttention) | `/slides/14-LLM-serving-part1.pdf` |
| 15 | `blackwell-tirx` | Week 9: Blackwell GPU and TIRx | `/slides/tirx-gemm/`（网页版） |
| 16 | `llm-serving-2` | Week 10: LLM Serving (Speculative Decoding) | `/slides/15-LLM-serving-part2.pdf` |
| 17 | `llm-finetuning` | Week 10: LLMs: Training (PEFT) | `/slides/16-LLM-finetuning.pdf` |
| 18 | `mixture-of-experts` | Week 11: LLMs: Mixture of Experts | `/slides/16-mixture-of-experts.pdf` |
| 19 | `advanced-ml-compilation` | Week 12: Advanced topics: ML Compilation | `/slides/advanced-topic-mlc.pdf` |
| 20 | `kernel-superoptimization` | Week 13: Advanced topics: ML Superoptimization | `/slides/18-kernel-superoptimization.pdf` |
| 21 | `mega-kernel` | Week 13: Advanced topics: Mega-Kernel | `/slides/19-mega-kernel.pdf` |

## 不计入的排期条目（说明为何 24 条 ⇒ 21 讲）

| 排期条目 | 为何不计入 |
| --- | --- |
| Week 2: MLK Jr Day. No Class. | 无课 |
| Week 14: Guest Lecture: Google TPU | **第三方客座**，不在授权范围 |
| Week 14: Guest Lecture: LLM Agents | **第三方客座**，不在授权范围 |
| Week 17: Final Poster Presentations | 非讲授单元 |

**⇒ 21 讲。**

## 备注

- 第 6、7 讲共用同一份 `06-CUDA-programming.pdf`（排期如此），**产出时按两页处理、内容切分不重叠**。
- 网页版讲义（`data_layout/` / `modern-gpu-gemm/` / `tirx-gemm/`）是**多文件目录**，
  取用时先列目录再定 `source_url`。
- 其余自制讲义（`07-transformers-attention` 等）**须先核对在 `lectures.yml` 排期内**才取；
  不在排期里的 PDF 视为第三方遗留，不译。
