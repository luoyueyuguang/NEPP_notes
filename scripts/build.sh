#!/usr/bin/env bash
# NEPP_notes 双版本构建脚本
#
# 为 408 与 math 各产出四个 PDF（构建在各自书目录内，文件名与发布命名一致）：
#   <book>-full.pdf       完整版：题目 + 解析（默认 \showsolutionstrue）
#   <book>-exercises.pdf  纯题目版：隐藏解析，每题解析处替换为 \answerarea 书写留白
#
# 纯题目版用 main.tex 的**临时副本**（sed 翻成 \showsolutionsfalse）编译，随后删除，
# 绝不修改源文件——避免 deep-dive 01 §5 记录的"sed 改源码留脏状态"风险。
#
# 每个版本编译两次：第一次生成 .aux/.toc，第二次收敛页码与书签。
# 编译后校验日志：硬错误（^!）失败；缺字符 / 重复标签告警；页数 sanity（exercises < full）。
#
# 用法：
#   scripts/build.sh            # 构建 408 + math 双版本
#   scripts/build.sh 408        # 只构建 408
#   scripts/build.sh math       # 只构建 math
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
# 任何退出路径都清掉纯题目版的临时驱动副本，避免仓库留脏。
trap 'rm -f "$ROOT/408/_build.tex" "$ROOT/math/_build.tex"' EXIT

# 从日志提取 "Output written on <file> (<n> pages" 中的页码 n。
pages() {
  grep -oE '\([0-9]+ pages' "$1" | grep -oE '[0-9]+' | head -1
}

# 编译一个版本（两次 pass），失败时从日志报错并终止。
compile_job() {
  local job="$1" target="$2" version="$3"
  local pass
  for pass in 1 2; do
    if ! xelatex -interaction=nonstopmode -halt-on-error -jobname="$job" "$target" \
        >/dev/null 2>&1; then
      echo "  ::error::$version ($job) xelatex pass $pass failed"
      grep '^!' "$job.log" 2>/dev/null | head -5 | sed 's/^/    /'
      return 1
    fi
  done
  return 0
}

# 校验单个 .log：硬错误失败，缺字符/重复标签告警。
check_log() {
  local log="$1" label="$2"
  if grep -q '^!' "$log" 2>/dev/null; then
    echo "  ::error::$label hard errors in $(basename "$log")"
    grep '^!' "$log" | head -5 | sed 's/^/    /'
    return 1
  fi
  grep -q 'Missing character' "$log" 2>/dev/null \
    && echo "  ::warning::$label Missing characters"
  grep -q 'multiply defined' "$log" 2>/dev/null \
    && echo "  ::warning::$label duplicate labels"
  echo "  $label OK"
}

build_book() {
  local book="$1"
  local dir="$ROOT/$book"
  local full="$book-full" ex="$book-exercises"
  local fullpages expages
  echo "===== $book ====="

  (
    cd "$dir" || return 1
    echo "[$book] full: $full.pdf"
    compile_job "$full" main.tex full || return 1
    echo "[$book] exercises: $ex.pdf"
    cp -f main.tex _build.tex || return 1
    sed -i 's/\\showsolutionstrue/\\showsolutionsfalse/' _build.tex || return 1
    compile_job "$ex" _build.tex exercises || return 1
    rm -f _build.tex
  ) || return 1
  rm -f "$dir/_build.tex"

  check_log "$dir/$full.log" "$book-full" || return 1
  check_log "$dir/$ex.log" "$book-exercises" || return 1

  fullpages="$(pages "$dir/$full.log")"
  expages="$(pages "$dir/$ex.log")"
  echo "  pages: $full=$fullpages  $ex=$expages"

  if [ -n "$fullpages" ] && [ -n "$expages" ]; then
    # 纯题目版因每题后叠加书写留白，篇幅可能不低于完整版，故仅报警；极端膨胀
    # （>1.3× 完整版）才视为异常（多半是解析未隐藏或留白失控）。
    if [ "$expages" -gt $((fullpages*13/10)) ]; then
      echo "  ::error::$book exercises ($expages) abnormally larger than full ($fullpages)"
      return 1
    elif [ "$expages" -ge "$fullpages" ]; then
      echo "  ::warning::$book exercises ($expages) >= full ($fullpages) (write-space makes it longer)"
    fi
  fi
  echo "  $book OK"
  return 0
}

main() {
  local targets=("$@") book
  [ ${#targets[@]} -eq 0 ] && targets=(408 math)
  for book in "${targets[@]}"; do
    if [[ "$book" != 408 && "$book" != math ]]; then
      echo "unknown book: $book (expected 408|math)" >&2
      FAIL=$((FAIL+1))
      continue
    fi
    if build_book "$book"; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
  done
  echo "===== summary: $PASS passed, $FAIL failed ====="
  [ "$FAIL" -eq 0 ]
}

main "$@"
