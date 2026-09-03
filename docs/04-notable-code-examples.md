# 04 · 优秀代码示例

> 本文档收录本仓库中真正值得复用的 LaTeX 工程技巧。每个示例给出"解决了什么问题 / 为什么值得关注 / 最小可运行示例 / 复用价值与局限"。
> 示例做了最小化处理，保留核心逻辑；完整源码以仓库实际文件为准。

---

## 示例 1：习题/解析双版本开关（全书核心机制）

**所在模块**：两书入口文件 + 全部章节/模拟卷文件。
**解决的问题**：同一份源文件要产出"纯题目版"和"题目+解析版"两个 PDF，且解析块散落在 300+ 处。

**为什么值得关注**：它用 TeX 展开期条件实现了"内容不变、视图切换"，是全书唯一的全局状态。

**最小示例**：

```latex
% 入口文件（定义一次，全局唯一）
\newif\ifshowsolutions
\showsolutionstrue      % 改 false 即隐藏全部解析

% 章节文件（每道题一个条件块）
\section{习题}
\subsection{基础过关题}

\textbf{1.} 求 $\lim\limits_{x \to 0} \dfrac{\sin 3x}{\tan 5x}$。

\ifshowsolutions%
\boxed{\textbf{解}} 当 $x \to 0$ 时，$\sin 3x \sim 3x$，$\tan 5x \sim 5x$，
故极限为 $\dfrac{3}{5}$。
\fi%

\medskip
```

**关键细节**：
- `\ifshowsolutions%` 行尾的 `%` 吃掉换行产生的空格，避免解析块位置出现多余空白；
- 数学章节用 `\boxed{\textbf{解}}` 起头、`\fi%` 收尾的"块式"写法；408 用 `\ifshowsolutions\par\noindent\textbf{解析：}...\fi` 的"行内段落式"写法——两种风格都可用，但同一本书内必须统一；
- 开关只能定义在入口文件。**历史教训**：408 曾有 5 个章节自行 `\showsolutionstrue` 导致全局关闭失效，已全部移除（408 REVIEW §6.1）。

**复用价值**：极高——任何"长文档按条件隐藏内容"的场景（答案、提示、教师版/学生版）都可套用。
**局限**：`\if...\fi` 内不能出现不成对的环境/分组，批量插入时需人工核对配对。

---

## 示例 2：tcolorbox 知识框体系（内容语义化）

**所在模块**：两书入口文件（`\newtcbtheorem` 系列）。
**解决的问题**：把"定义/公式/结论/警示/例题"五类知识语义可视化为不同配色的框，读者一眼分辨内容层级。

**最小示例（math 侧）**：

```latex
\usepackage[skins, breakable, theorems]{tcolorbox}

\newtcbtheorem[number within=section]{mydef}{定义}%
  {colback=blue!5, colframe=cyan!60!blue, fonttitle=\bfseries}{th}

\newtcbtheorem[number within=section]{formula}{公式}%
  {colback=blue!5, colframe=white!30!pink,
   fonttitle=\bfseries, coltitle=cyan!30!black, breakable}{fo}

\newtcbtheorem[number within=section]{conclusion}{结论}%
  {colback=blue!5, colframe=blue!50!black, fonttitle=\bfseries, breakable}{cu}
```

```latex
% 使用方式（章节文件）——只写语义，不写样式
\begin{mydef}{数列极限的定义}{definition of limit}
    \(\lim\limits_{n \to \infty} x_n = A
     \Leftrightarrow \forall \varepsilon > 0, \exists N, \dots\)
\end{mydef}
```

**408 侧的进阶做法**：所有框共享一个 `studybox` 基础样式（圆角、可跨页、统一间距），再按语义叠加配色与 `borderline west` 左强调线——"基础样式 + 语义增量"的组合优于每类框独立定义。

**复用价值**：极高，是"语义化排版"的范式。
**局限**：`\newtcbtheorem` 环境体内部不能嵌套未定长参数；框计数器与 `\counterwithin` 联动需在入口文件统一配置。

---

## 示例 3：408 自定义封面（tikz 整页绘制）

**所在模块**：`408/main.tex` 的 `\makecustomcover`。
**解决的问题**：默认 `\maketitle` 无法表达"书籍产品"的视觉定位，需要全页深色封面。

**为什么值得关注**：展示了 tikz 的 `remember picture, overlay` 全页定位技巧——不引入任何图片素材，纯矢量绘制，仓库自包含。

**最小示例**：

```latex
\newcommand{\makecustomcover}{%
\pagecolor{NavyDark}
\begin{titlepage}
  \thispagestyle{empty}
  \begin{tikzpicture}[remember picture, overlay]
    % 全页底色
    \fill[NavyDark] (current page.south west) rectangle (current page.north east);
    % 右上角斜角色块
    \fill[Teal] ([xshift=-3.2cm]current page.north east) --
                (current page.north east) --
                ([yshift=-6.8cm]current page.north east) -- cycle;
    % 底部色条
    \fill[Navy] (current page.south west) rectangle
                ([yshift=2.2cm]current page.south east);
    % 内边框
    \draw[white!10, line width=0.7pt]
      ([xshift=1.5cm,yshift=-1.5cm]current page.north west) rectangle
      ([xshift=-1.5cm,yshift=1.5cm]current page.south east);
  \end{tikzpicture}
  \vspace*{2.4cm}
  \begin{flushleft}
    {\color{white}\sffamily\bfseries\fontsize{48pt}{54pt}\selectfont 408}\par
    {\color{white!72}\sffamily\fontsize{15pt}{22pt}\selectfont
      系统复习讲义 · 章节训练 · 三套模拟卷}\par
  \end{flushleft}
\end{titlepage}
\pagecolor{white}
}
```

**关键细节**：`\pagecolor` 在 titlepage 前后切换，避免深色页面污染正文；封面后正文用 `\pagenumbering{Roman}` 起目录、`\clearpage` 后 `\pagenumbering{arabic}` 转正文页码——页面叙事完整。

**复用价值**：高——任何需要"无素材封面"的 XeLaTeX 书籍项目。
**局限**：`fontsize{48pt}` 等硬编码字号在纸张尺寸变化时需调整；颜色名依赖入口文件 `\definecolor`。

---

## 示例 4：代码块内数学公式混排（listings escapeinside）

**所在模块**：`408/main.tex` 的 `\lstset`。
**解决的问题**：C 代码里需要出现数学公式（如复杂度注释），而 listings 的字符处理会破坏 `$...$`。

**最小示例**：

```latex
\lstset{
  language=C,
  breaklines=true,
  escapeinside={\%*}{*)},   % 代码中的 %* ... *) 段交给 LaTeX 排版
  % ... 其余样式
}

\begin{lstlisting}[language=C]
// 平均比较次数 %*$(n+1)/2$*)，时间复杂度 %*$O(n)$*)
for (int i = 0; i < L.length; i++)
    if (L.data[i] == e) return i + 1;
\end{lstlisting}
```

**复用价值**：中高——需要"代码+公式混排"的讲义必备。
**局限**：`escapeinside` 的定界符要避开 C 语言本身的语法（`%` 不是 C 运算符所以安全）；转义段内不能再嵌套 lstlisting。

---

## 示例 5：全局粗体重定义（math 的视觉语言）

**所在模块**：`math/main.tex`。
**解决的问题**：数学笔记中 `\textbf` 的使用频率极高，默认黑体与正文区分度不足，作者希望全书粗体统一为"蓝色无衬线"。

**最小示例**：

```latex
\renewcommand{\textbf}[1]{\textcolor{blue}{\textsf{#1}}}
```

**为什么值得关注**：一行命令改变全书视觉——全局钩子（global hook）模式。
**复用价值**：低（这是高度个人化的审美决策，且重定义 `\textbf` 有副作用风险）。
**局限**：`\textbf` 在标题、目录、索引中也被重定义，可能产生非预期配色；408 侧选择了更克制的"用 `\sffamily\bfseries\color{Navy}` 逐级定制标题"，而不是全局重定义——后者的工程风险更小。

---

## 示例 6：编译质量门禁（CI 静态检查）

**所在模块**：`.github/workflows/build.yml`。
**解决的问题**：LaTeX 编译的"软失败"——即使有错误也会输出 PDF，需要机械检查保证质量。

**最小示例**：

```bash
xelatex -interaction=nonstopmode -halt-on-error -output-directory=out main.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=out main.tex

# 硬错误检查
if grep -q '^!' out/main.log; then
  echo "::error::LaTeX compilation had hard errors"
  exit 1
fi

# 缺字检查（警告级）
grep -q 'Missing character' out/main.log && echo "::warning::Missing characters"

# 重复标签检查（警告级）
grep -q 'multiply defined' out/main.log && echo "::warning::Duplicate labels"
```

**复用价值**：高——三行 grep 覆盖了 LaTeX 最常出现的三类质量事故（错误、缺字、标签冲突）。
**局限**：`grep '^!'` 只匹配行首硬错误；Overfull/Underfull 这类排版警告不阻断构建（本仓库当前仍有少量，属可接受范围）。
