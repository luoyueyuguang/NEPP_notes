#!/usr/bin/env bash
# scripts/check_chapter.sh <tag> <book> <chapterpath>
#   Compile ONE chapter file in isolation against the book's real preamble.
#   Usage: scripts/check_chapter.sh math-c1 math calculus/chap1.tex
#          scripts/check_chapter.sh ds-c3   408 ds/chap3.tex
#   <tag> must be unique per concurrent caller (used for jobname/harness filename).
set -uo pipefail

tag="${1:?tag}" book="${2:?book}" chap="${3:?chapter}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/$book"
if [ ! -d "$DIR" ]; then echo "::error::unknown book $book"; exit 2; fi

HARNESS="$DIR/_chk_$tag.tex"

# build a standalone driver: full preamble (everything before \begin{document})
# + \providecommand{\Chap}{<chapter>} + a one-chapter body.
awk '/^\\begin\{document\}/{exit} {print}' "$DIR/main.tex" > "$HARNESS"
printf '%s\n' \
  "\\providecommand{\\Chap}{$chap}" \
  '\begin{document}' \
  '\input{\Chap}' \
  '\end{document}' >> "$HARNESS"

rc=0
for pass in 1 2; do
  if ! (cd "$DIR" && xelatex -interaction=nonstopmode -halt-on-error \
        -jobname="_chk_$tag" "$(basename "$HARNESS")" >/dev/null 2>&1); then
    rc=1
    break
  fi
done

echo "===== $book/$chap ====="
if [ "$rc" -ne 0 ]; then
  echo "::error::COMPILE FAILED"
  grep -E '^!' "$DIR/_chk_$tag.log" 2>/dev/null | head -20
else
  echo "::ok::compiled"
  grep -oE '\([0-9]+ pages' "$DIR/_chk_$tag.log" 2>/dev/null | head -1
fi

# tidy aux files for this tag
rm -f "$HARNESS" "$DIR/_chk_$tag.aux" "$DIR/_chk_$tag.toc" "$DIR/_chk_$tag.out" "$DIR/_chk_$tag.log" "$DIR/_chk_$tag.pdf"
exit "$rc"
