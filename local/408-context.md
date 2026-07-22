# 408 讲义编写规范

## 目标
编写考研 408 计算机学科专业基础综合的系统复习讲义。每章面向 408 应试，但以高质量教材为内容主干（非王道/天勤）。

## 教材体系
- 数据结构：邓俊辉《数据结构（C++语言版）》+ Sedgewick《算法》第4版
- 组成原理：Patterson&Hennessy《计算机组成与设计》+ CS:APP
- 操作系统：OSTEP + 陈海波《现代操作系统：原理与实现》
- 计算机网络：Kurose《计算机网络：自顶向下方法》+ 谢希仁（仅术语对齐）

## 408 考试结构
- 满分150分，180分钟
- 数据结构45分，组成原理45分，操作系统35分，计算机网络25分
- 40道单选(80分) + 7道综合应用题(70分)

## LaTeX 样式
参考 `408/ds/chap1.tex`。必须使用以下环境：
- `\begin{mydef}{标题}{label}` — 定义框
- `\begin{formula}{标题}{label}` — 要点框
- `\begin{conclusion}{标题}{label}` — 结论框
- `\begin{attention}...\end{attention}` — 注意事项
- `\begin{tablebox}{标题}...\end{tablebox}` — 表格
- `\begin{lstlisting}[language=C]...\end{lstlisting}` — 代码
- `\boxed{\textbf{例}}` — 例题标记

## 每章结构
1. 概念定义（mydef/attention 框）
2. 核心算法/性质（formula/conclusion 框，含代码）
3. 基础过关题（6-8道，单选+填空+简答）
4. 真题风格与综合训练（4-6道，含综合题）
5. 拓展阅读（标注对应教材精确章节）

## 编写要求
- 语言精炼，不含"王道说""天勤认为"等字样
- 代码用 C 语言，风格参考邓俊辉教材
- 408 重点考点用 attention 框突出
- 每章末尾标注教材参考章节
- 不要用 minted（用 listings）
- tikz 图用于数据结构（链表、树、图）和组成原理（数据通路）
