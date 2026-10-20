#!/bin/bash
# Build the per-pattern diagrams: diagrams/<name>.tex -> images/<name>.pdf (paper)
# and images/<name>.svg (site, text as paths). Rebuilds a diagram only when its
# source or style.tex is newer than its PDF. Needs xelatex (MacTeX) and pdftocairo (poppler).
#   ./build.sh            changed diagrams
#   ./build.sh name ...   only these (forced)
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/Library/TeX/texbin:$PATH"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

if [ $# -gt 0 ]; then names=("$@"); force=1
else names=($(ls *.tex | grep -v '^style\.tex$' | sed 's/\.tex$//')); force=0; fi

for name in "${names[@]}"; do
  pdf="../images/$name.pdf"
  if [ $force = 1 ] || [ ! -f "$pdf" ] || [ "$name.tex" -nt "$pdf" ] || [ style.tex -nt "$pdf" ]; then
    echo "diagram $name..."
    xelatex -interaction=nonstopmode -halt-on-error -output-directory="$tmp" "$name.tex" > "$tmp/$name.log" \
      || { tail -20 "$tmp/$name.log"; exit 1; }
    pdftocairo -svg "$tmp/$name.pdf" "../images/$name.svg"
    cp "$tmp/$name.pdf" "$pdf"
    # the paper's text block is 15.2 cm; a wider diagram runs into the margin
    w=$(pdfinfo "$pdf" | awk '/Page size/ {printf "%.1f", $3/72*2.54}')
    awk -v w="$w" 'BEGIN { exit !(w > 15.0) }' && echo "  WARNING: $name is $w cm wide (max 15.0)" || true
  fi
done
