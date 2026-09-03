# NEPP_notes

> ⚠️ **免责声明：本项目内容完全由 AI 生成，仅供学习参考，不负任何准确性、完整性或可靠性责任。使用者自行承担因使用本项目内容产生的一切后果。**

## 内容

### 408 计算机学科专业基础综合

- 数据结构（8 章）、计算机组成原理（7 章）、操作系统（6 章）、计算机网络（6 章）
- 三套模拟卷（40 单选 + 7 综合，150 分 / 180 分钟）
- 完整版 378 页 / 纯题目版 374 页（习题与解析分离，纯题目版每道题后留有手写答题空间，见 [发布](#发布)）

### 考研数学一

- 高等数学（9 章）、线性代数（7 章）、概率论与数理统计（7 章）
- 三套模拟卷（10 单选 + 6 填空 + 6 解答，150 分 / 180 分钟）
- 完整版 471 页 / 纯题目版 376 页（纯题目版每道题后留有手写答题空间）
- 数学部分在编写中参考了李正元老师的复习全书等资料，特此致谢。

## 文档

详细的项目文档（架构、设计思想、接口语义、构建发布、编写规范与深挖专题）见 [`docs/`](docs/) 目录：

| 文档 | 内容 |
|---|---|
| [00 · 项目总览](docs/00-project-overview.md) | 项目是什么、仓库布局、规模、阅读顺序 |
| [01 · 技术架构](docs/01-technical-architecture.md) | 构建体系、文档组装链、配置、扩展点 |
| [02 · 设计原因与工程思想](docs/02-design-rationale-and-engineering-philosophy.md) | 设计哲学、技术取舍、优劣分析 |
| [03 · 产品与交互分析](docs/03-product-and-interaction-analysis.md) | 使用场景、刷题工作流、业务规则 |
| [04 · 优秀代码示例](docs/04-notable-code-examples.md) | 开关机制、知识框、封面、CI 等可复用范例 |
| [05 · 接口语义文档](docs/05-interface-semantics.md) | 全部自定义 LaTeX 环境/命令的接口说明 |
| [06 · 构建与发布指南](docs/06-build-and-release-guide.md) | 构建、双版本、Release 发布、CI 说明 |
| [07 · 内容编写规范与质量保障](docs/07-content-standards-and-review.md) | 编写约束、审阅方法、验收清单 |
| [Deep Dive · 解析开关机制](docs/deep-dives/01-solutions-toggle-mechanism.md) | 习题/解析双版本机制的完整剖析 |
| [Deep Dive · 习题体系与答案闭环](docs/deep-dives/02-exercise-system-and-answer-closure.md) | 习题组织、逐题闭环工程、唯一性治理 |
| [Deep Dive · 模拟卷设计](docs/deep-dives/03-exam-paper-design.md) | 卷面结构、难度分层、真题风格边界 |

另见 `math/REVIEW.md`（数学四轮审阅报告）与 `408/REVIEW.md`（408 多轮审阅报告），记录全部正确性修订与复算证据。

## 构建

```bash
cd 408  # 或 cd math
xelatex -interaction=nonstopmode -halt-on-error -output-directory=out main.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=out main.tex
```

构建双版本（纯题目版 / 完整版）与发布 Release 的完整流程见 [06 · 构建与发布指南](docs/06-build-and-release-guide.md)。

## 发布

GitHub Releases 同时提供两本书的纯题目版与完整版（习题/解析分离，刷题时不泄题）：

- `*-exercises.pdf` — 纯题目版
- `*-full.pdf` — 题目 + 解析版

最新版本见 [Releases](https://github.com/luoyueyuguang/NEPP_notes/releases)。

## 版权声明

本项目内容由 AI 生成，仅供个人学习参考。数学部分参考了李正元老师的资料，408 部分参考了邓俊辉、Patterson \& Hennessy、OSTEP、Kurose 等教材。如有无意侵权，请在 [Issues](https://github.com/luoyueyuguang/NEPP_notes/issues) 中提出，作者将尽快处理。
