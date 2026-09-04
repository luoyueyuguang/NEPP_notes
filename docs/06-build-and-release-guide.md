# 06 · 构建与发布指南

> 面向维护者：如何从源码构建 PDF、如何生成双版本、如何发布 GitHub Release、CI 如何工作。

## 1. 环境要求

| 依赖 | 用途 | 安装（Ubuntu/Debian） |
|---|---|---|
| TeX Live（xelatex） | 编译引擎 | `texlive-xetex texlive-latex-recommended texlive-latex-extra` |
| CJK 支持 | ctexbook 文档类 | `texlive-lang-chinese` |
| 字体 | Noto Serif / Sans / Mono + CJK | `fonts-noto fonts-noto-cjk` |
| 辅助包 | tikz/pgfplots/tcolorbox/listings 等 | `texlive-fonts-recommended texlive-fonts-extra` |

> CI 使用的完整安装清单见 `.github/workflows/build.yml`（含 latexmk，但实际构建仍直接调 xelatex）。

## 2. 基础构建（单版本）

```bash
# 数学
cd math
xelatex -interaction=nonstopmode -halt-on-error -output-directory=out main.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=out main.tex

# 408
cd 408
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

**为什么编译两次**：第一次生成 `.aux`（引用、计数器）与 `.toc`（目录），第二次收敛页码与书签。跳过第二次会出现"Label(s) may have changed"警告和错误的目录页码。

**差异提示**：
- math 用 `-output-directory=out`（CI 同款）；408 直接输出到源目录（构建产物被 .gitignore 忽略，除 `math/out/main.pdf` 外无版本控制风险）；
- 构建成功后检查日志：`grep '^!' main.log` 应无输出（硬错误），`Missing character` 与 `multiply defined` 应尽量为 0。

## 3. 双版本构建（习题版 / 完整版）

核心原理：`main.tex` 中的 `\showsolutionstrue` 是唯一开关。翻转它并用不同 `-jobname` 输出两个 PDF。

```bash
cd math

# 版本 A：纯题目（隐藏解析）
sed -i 's/\\showsolutionstrue/\\showsolutionsfalse/' main.tex
xelatex -interaction=nonstopmode -halt-on-error -jobname=math-exercises main.tex
xelatex -interaction=nonstopmode -halt-on-error -jobname=math-exercises main.tex

# 版本 B：题目+解析（记得把开关改回来！）
sed -i 's/\\showsolutionsfalse/\\showsolutionstrue/' main.tex
xelatex -interaction=nonstopmode -halt-on-error -jobname=math-full main.tex
xelatex -interaction=nonstopmode -halt-on-error -jobname=math-full main.tex
```

**⚠️ 风险控制**：`sed` 改源码属于临时状态修改——若两步之间构建中断，仓库会留下 `\showsolutionsfalse` 的脏状态。建议：
1. 构建前 `git status` 确认工作区干净；
2. 构建后立即恢复开关并 `git diff` 验证无残留；
3. **推荐**：直接用 `scripts/build.sh`（见下），它用 `main.tex` 的*临时副本*翻开关，绝不改动源文件。

**推荐方式（自动双版本 + 校验）**：仓库提供了 `scripts/build.sh`，一次构建两本书的双版本并在编译后校验（硬错误失败，缺字符/重复标签告警，页数 sanity `exercises < full`）：

```bash
scripts/build.sh            # 构建 408 + math 双版本（4 个 PDF）
scripts/build.sh 408        # 只构建 408
scripts/build.sh math       # 只构建 math
```

`scripts/check_solutions.py` 是纯题目版正确性的静态回归哨兵（纯 Python、无需 LaTeX）：校验所有 `\ifshowsolutions` 解析块配对、无"环境跨过 `\fi` 边界"的孤儿结构、且都带 `\else \answerarea` 书写留白。CI 每次构建前先跑它。

```bash
python3 scripts/check_solutions.py   # 有问题时退出码非 0
```

**版本命名约定**（与 v1.2.0 发布一致）：

| 文件 | 内容 | 实测页数（2026-09-04） |
|---|---|---|
| `math-exercises.pdf` | 数学 · 纯题目（含手写留白） | 384 |
| `math-full.pdf` | 数学 · 题目+解析 | 471 |
| `408-exercises.pdf` | 408 · 纯题目（含手写留白） | 382 |
| `408-full.pdf` | 408 · 题目+解析 | 378 |

## 4. 发布 GitHub Release

前置：双版本 PDF 已生成并复制到 `release/` 目录。

```bash
# ① 提交并推送（release/*.pdf 需强制跟踪，见 .gitignore）
git add release/*.pdf -f
git commit -m "release: vX.Y.Z"
git push

# ② 创建 Release（gh CLI 已登录）
gh release create vX.Y.Z \
  release/math-exercises.pdf \
  release/math-full.pdf \
  release/408-exercises.pdf \
  release/408-full.pdf \
  --title "NEPP_notes vX.Y.Z — 版本说明" \
  --notes "## 更新内容 ..."
```

**历史发布**：
- `v1.1.0`（2026-07-22）：每本书单一 PDF；
- `v1.2.0`（2026-07-31）：习题/解析分离，每本书两个 PDF；
- `v1.3.0`（2026-09-03）：纯题目版每道题后加书写留白（`\answerarea`）。

## 5. CI 行为说明

`.github/workflows/build.yml`（覆盖 408 与 math 双版本）：

```mermaid
flowchart LR
    A[push / PR → main] --> B[checkout]
    B --> C[安装 TeX Live + Noto 字体]
    C --> D[python3 scripts/check_solutions.py 静态哨兵]
    D -->|配对/孤儿/留白异常| E[::error:: 失败]
    D -->|OK| F[bash scripts/build.sh]
    F --> G{xelatex ×2 每版本}
    G --> H[输出 4 个 PDF]
    F --> I{日志校验}
    I -->|硬错误 ^!| J[::error:: 失败]
    I -->|Missing character| K[::warning::]
    I -->|multiply defined| L[::warning::]
    F --> M[上传 4 个 PDF artifact 保留 7 天]
```

**说明**：
- CI 现在构建**两本书的双版本**：`scripts/build.sh` 用 `main.tex` 临时副本翻 `\showsolutionsfalse`，绝不改动源文件；
- 静态哨兵 `scripts/check_solutions.py` 在编译前先跑，任何解析块配对/孤儿环境/缺书写留白都会直接失败；
- 纯题目版页数必须小于完整版（`exercises < full`），否则视为异常。

**已知缺口**：
- artifact 不自动发布为 Release（发布仍手工 gh CLI）；
- 不检查 Overfull/Underfull（排版警告量大，会淹没信号）。

## 6. 常见问题排查

| 症状 | 原因 | 处理 |
|---|---|---|
| `! LaTeX Error: File 'ctexbook.cls' not found` | 缺 `texlive-lang-chinese` | 安装后重试 |
| 中文显示为方块 | 缺 CJK 字体 | 安装 `fonts-noto-cjk` |
| `Font shape ... not available` | 字体形状回退 | 非致命，可忽略（中文斜体回退已知） |
| 目录页码错误 | 只编译了一次 | 再编译一次 |
| `Label(s) may have changed` | 同上 | 再编译一次 |
| `\ifshowsolutions` 未定义 | 在子文件单独编译（脱离了 main.tex） | 必须从 main.tex 整书编译 |
| 解析仍然显示（开关已关） | 子章节重复定义了开关 | 全局搜索删除局部 `\newif`/`\showsolutionstrue`（历史教训） |
| 编译卡死/内存不足 | tikz-feynman 等大图 | 使用 `-halt-on-error` 定位；必要时增加 TeX 内存（math/main.tex 头部有 `extra_mem_top` 注释示例） |
