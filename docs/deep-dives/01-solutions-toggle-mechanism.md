# Deep Dive 01 · 习题/解析开关机制

> 专题深挖：`\ifshowsolutions` 从设计、实现、历史教训到发布流水线的完整机制。

## 1. 解决什么问题

两本书合计 470+ 道章节习题和 200+ 道模拟卷题目，每道题的解析紧跟在题干之后。用户需求非常具体："写题的时候就可以看到答案了"——即刷题版 PDF 必须不含任何解析。需求拆解：

1. 同一份源码要能产出"含解析"和"不含解析"两种 PDF；
2. 解析必须**物理消失**（不是白字/透明——那会泄露信息且浪费页数）；
3. 开关必须全局一致（不能出现"这章关了那章还开着"）；
4. 内容维护者写题时零心智负担（默认把解析放进条件块即可）。

## 2. 实现机制

### 2.1 单一定义点

```latex
% 各自主 main.tex，全文唯一
\newif\ifshowsolutions
\showsolutionstrue          % 或 \showsolutionsfalse
```

`\newif` 在 TeX 中生成 `\ifshowsolutions` 条件原语 + `\showsolutionstrue/false` 两个赋值命令。

### 2.2 消费端三种风格

| 风格 | 语法 | 使用位置 |
|---|---|---|
| math 章节块式 | `\ifshowsolutions%` ... `\fi%` | math 全部章节（335 处） |
| 408 段落式 | `\ifshowsolutions\par\noindent\textbf{解析：}...\fi` | 408 章节与模拟卷 |
| exams 紧凑式 | `\ifshowsolutions\par\noindent\textbf{解析：}...\boxed{\textbf{答案：}(B)}\fi` | 两书模拟卷 |

408 段落式的关键细节：`\par\noindent` 在条件成立时开启新段落，`\boxed{\textbf{答案：}(B)}` 把最终答案框出——答案和解析在同一条件块内，一并隐藏。

### 2.3 展开期行为

`\ifshowsolutions` 在 **TeX 展开期**求值，不是渲染期过滤：

```
false 时：\ifshowsolutions <解> \else \answerarea \fi —— 解析跳过，改为输出书写留白区
true  时：<解> 原样进入页面流，留白区（\else 分支）被自动跳过
```

自 2026-09-03 起，纯题目版不再"解析消失后紧贴下题"，而是把每道被隐藏的解析替换为 `\answerarea`（三条书写横线），给做题留下手写空间；完整版经由 `\else` 分支自动跳过留白区，排版不受影响。

这带来两个可观测效果：
- **页数变化**：纯题目版"隐藏解析 + 叠加书写留白"后篇幅接近甚至超过完整版。当前工作树实测 math-full 471 → math-exercises 384 页、408-full 378 → 408-exercises 382 页；无留白的旧基线为 math 462→327、408 371→325；
- **排版稳定**：条件块外的 `\vspace{8pt}`、`\medskip` 间距命令保留，习题页不塌陷。

> 注意：`\answerarea` 必须放在解块内的 `\else` 分支；若某解块把 `\begin{enumerate}` 开在开关内、把 `\end{enumerate}` 放在 `\fi` 之后，隐藏解析会留下"孤儿 `\end{...}`"。这类跨边界环境必须把 `\fi`（连同 `\else \answerarea`）移到 `\end{...}` 之后（见 §6）。

## 3. 历史教训（408 REVIEW §6.1 记录）

> "发现 5 个子章节重复声明并强制执行 `\showsolutionstrue`，导致主入口即使设置隐藏解析，后续章节仍会自行重新打开。现已移除局部声明，解析开关只在 `main.tex` 定义和控制。"

**根因分析**：早期章节作者在文件头部自行写了 `\newif\ifshowsolutions` + `\showsolutionstrue`（可能是为了单独编译该章调试）。`\newif` 重复定义虽不报错（TeX 静默重定义），但 `\showsolutionstrue` 的赋值**覆盖**了主入口的全局设置——于是"关开关"只对没写局部声明的章节生效。

**防范规则**（已写入 `07` 文档与验收清单）：
1. 子文件永不出现 `\newif`；
2. 子文件永不调用 `\showsolutionstrue/false`；
3. 全局搜索 `grep -rn "newif.*showsolutions"` 作为发布前检查。

## 4. math 侧的批量接入工程（2026-07-31）

math 原无开关，本次接入分三步：

1. **入口改造**：`math/main.tex` 加 `\newif\ifshowsolutions` + `\showsolutionstrue`；`math/exams.tex` 删除自带的 `\newif\ifshowsolutions`（原文件自声明，保留会与主入口重复定义）；
2. **批量包裹**：对 26 个章节文件，用脚本识别 `\boxed{\textbf{解}}` / `\boxed{\textbf{证明}}` / `\boxed{\textbf{答案}}` 起始行，向前插 `\ifshowsolutions%`、向后插 `\fi%`——共 335 处；
3. **终止条件设计**：脚本需要判断"解析块到哪结束"。采用结构化终止符：`\subsection` / `\section` / `\item` / `\end{enumerate}` / `\newpage` / 下一个编号题 `\textbf{N.}` / 下一个题型 `\textbf{（`。⚠️ 关键坑：不能把 `\textbf{` 一律当终止符——解析正文里的 `\textbf{分析：}`、`\textbf{反例：}`、`\textbf{注：}` 是内容不是新题，必须排除。

**教训**：这类批量改写必须（1）先 `git checkout` 恢复基线再重跑（脚本幂等性不可信）；（2）抽样人工核对（重点核对"分析/注/反例"这类内嵌粗体是否被错误截断）。

## 5. 发布流水线

构建已由 `scripts/build.sh` 自动化，不再手工 `sed` 翻开关：

```mermaid
flowchart LR
    A[scripts/check_solutions.py 静态哨兵] --> B
    B[scripts/build.sh 双版本] --> C[构建 4 个 PDF]
    C --> D[release/ 目录]
    D -->|git add -f| E[commit + push]
    E -->|gh release create| F[GitHub Release]
```

**实现**：`scripts/build.sh` 对每本书先编译完整版（`-jobname=<book>-full`），再用 `main.tex` 的**临时副本**（`sed` 翻成 `\showsolutionsfalse`）编译纯题目版（`-jobname=<book>-exercises`），结束后删除副本——全程不触碰源文件，规避了"sed 改源码留脏"风险。编译后校验日志（硬错误失败，缺字符/重复标签告警，页数 sanity `exercises < full`）。

**风险点**：
- `release/*.pdf` 被 `*.pdf` gitignore 覆盖，必须 `git add -f` 强制跟踪；
- 两书四文件一次性发布，版本号递增（v1.1.0 → v1.2.0 → v1.3.0）；
- `scripts/check_solutions.py` 是纯题目版正确性的回归哨兵：解析块必须配对、无"环境跨过 `\fi`"的孤儿结构、且都带 `\else \answerarea`。新增解块时违背任一条，脚本/CI 会直接报错（杜绝 §6 记录的那类 `Lonely \item`）。

## 6. 扩展思考

- **局部开关需求**（如"只看这章的解析"）：当前机制不支持——如需此能力，可在 `\showsolutions` 之外增加按章的二级开关，但复杂度显著上升，且违背"单一全局状态"原则，不建议；
- **教师版/学生版场景**：本机制可直接复用（教师版开、学生版关）；
- **自动化**：双版本构建可封装 `scripts/release.sh` 或 CI 双 job，消除手工 sed 风险（见 `06` 文档）；
- **验证手段**：发布后对比两版页数与文件大小（当前基线 math 384/471、408 382/378），异常波动说明解析块配对出错或书写留白未正确替换；
- **书写留白（2026-09-03）**：纯题目版在 `\ifshowsolutions` 的 `\else` 分支输出 `\answerarea`（`main.tex` 统一定义），给做题留出横线书写空间。落地时发现 16 处数学解块存在"`\begin{enumerate}`…在开关内、`\end{enumerate}` 在 `\fi` 之后"的跨边界结构，隐藏解析会导致孤儿 `\end{...}`——已逐个把 `\fi`（连同 `\else \answerarea`）移到对应 `\end{...}` 之后。408 无此问题。新增解块时须保证环境成对包在开关内，否则纯题目版会报 `Lonely \item`。
