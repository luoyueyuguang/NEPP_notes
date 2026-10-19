#!/usr/bin/env python3
"""静态校验 NEPP_notes 的 \\ifshowsolutions 解析块（纯题目版正确性的回归哨兵）。

对每个 .tex（排除 main.tex 驱动，其只声明开关）检查：
  1. 配对：未注释的 `\\ifshowsolutions` 数量 == `\\fi` 数量；
  2. 无孤儿环境：`\\begin{env}` 开在解析块内、`\\end{env}` 在 `\\fi` 之后——
     此跨边界结构在纯题目版（\\showsolutionsfalse）隐藏解析时会留下孤儿 `\\end{...}`，
     触发 `Lonely \\item` / `Extra \\end{...}`；
  3. 书写留白：每个解析块都带 `\\else \\answerarea`（缺失则纯题目版没有手写空间）。

用法：scripts/check_solutions.py
退出码非 0 表示发现问题。
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IFSOL = re.compile(r"\\ifshowsolutions\b")
FI = re.compile(r"\\fi\b")
BEG = re.compile(r"\\begin\{([^}]+)\}")
END = re.compile(r"\\end\{([^}]+)\}")
TOKEN_RE = re.compile(
    r"\\ifshowsolutions\b|\\fi\b|\\answerarea\b|\\begin\{[^}]+\}|\\end\{[^}]+\}"
)
# 解答标记不得出现在开关之外（纯题目版会原样排版）。
SOLUTION_MARK_RE = re.compile(
    r"\\boxed\{\s*(?:\\textbf\{\s*(?:解|证明|答案)|\\text\{\s*(?:\\textbf\{\s*)?(?:解|证明|答案))"
)


def outside_solution_marks(lines, toks):
    """Return line numbers of solution boxes outside any \\ifshowsolutions block."""
    marks = []
    depth = 0
    tok_i = 0
    for ln, line in enumerate(lines):
        pre = active(line)
        # Count toggles on this line before testing the line's content.
        opens = len(re.findall(r"\\ifshowsolutions\b", pre))
        closes = len(re.findall(r"\\fi\b", pre))
        if (
            depth == 0
            and "\\ifshowsolutions" not in pre
            and SOLUTION_MARK_RE.search(pre)
        ):
            marks.append(ln + 1)
        depth += opens - closes
        if depth < 0:
            depth = 0
    return marks


def active(line):
    i = 0
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "%":
            return line[:i]
        i += 1
    return line


def scan(path):
    """Return (errors:list[str], n_blocks)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    toks = []
    for ln, line in enumerate(lines):
        pre = active(line)
        for m in TOKEN_RE.finditer(pre):
            toks.append((ln, m.group(0)))

    errors = []
    for ln in outside_solution_marks(lines, toks):
        errors.append(
            f"{path}:{ln}: solution box outside \\ifshowsolutions "
            f"(would leak into the exercise build)"
        )
    blocks = 0
    # Process each \\ifshowsolutions block (no nesting of the toggle is allowed).
    i, n = 0, len(toks)
    while i < n:
        if toks[i][1] != "\\ifshowsolutions":
            i += 1
            continue
        start_ln = toks[i][0]
        blocks += 1
        # Walk forward to the matching \\fi (first \\fi; nesting is prohibited).
        j = i + 1
        envstack = []
        has_else_aa = False
        while j < n:
            t = toks[j][1]
            if t == "\\fi":
                break
            if t == "\\answerarea":
                has_else_aa = True
                j += 1
                continue
            m = BEG.match(t)
            if m:
                envstack.append(m.group(1))
            else:
                m = END.match(t)
                if m:
                    e = m.group(1)
                    if envstack and envstack[-1] == e:
                        envstack.pop()
                    elif e in envstack:
                        envstack.remove(e)
            j += 1
        else:
            # reached EOF without a \\fi
            errors.append(f"{path}:{start_ln+1}: unmatched \\ifshowsolutions (no \\fi)")
            i = n
            continue
        end_ln = toks[j][0]
        block_text = "\n".join(lines[start_ln : end_ln + 1])
        is_solution = ("\\boxed" in block_text) or ("解析" in block_text) or ("解答" in block_text)
        if is_solution and not has_else_aa:
            errors.append(f"{path}:{start_ln+1}: block lacks '\\else \\answerarea'")
        if envstack:
            errs = ", ".join(sorted(set(envstack)))
            errors.append(
                f"{path}:{start_ln+1}: environment(s) opened inside block but closed "
                f"after \\fi (orphan): {errs}"
            )
        i = j + 1
    return errors, blocks


def main():
    files = []
    for root_dir in ("408", "math"):
        files += glob.glob(os.path.join(ROOT, root_dir, "**", "*.tex"), recursive=True)
    files = sorted(
        set(
            f
            for f in files
            if not f.endswith("main.tex")
            and not os.path.basename(f).startswith("_")
        )
    )

    errors = []
    total_blocks = 0
    for path in files:
        errs, blocks = scan(path)
        total_blocks += blocks
        errors.extend(errs)

    if errors:
        print(f"FOUND {len(errors)} issue(s):", file=sys.stderr)
        for e in errors[:50]:
            print("  " + e, file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors)-50} more", file=sys.stderr)
        print(f"checked {len(files)} files, {total_blocks} solution blocks", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {len(files)} files, {total_blocks} solution blocks balanced & have answerarea")


if __name__ == "__main__":
    main()
