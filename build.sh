#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
case "${1:-all}" in
  all) languages=(en zh) ;;
  en|zh) languages=("$1") ;;
  *) echo "Usage: bash build.sh [all|en|zh]" >&2; exit 2 ;;
esac
command -v xelatex >/dev/null || { echo "XeLaTeX is required." >&2; exit 1; }
for lang in "${languages[@]}"; do
  work="$root/.build/$lang"
  mkdir -p "$work"
  (
    cd "$root/$lang"
    for doc in manuscript supplement title_page; do
      for pass in 1 2 3; do
        if ! xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory="$work" "$doc.tex" >"$work/$doc.pass$pass.stdout" 2>&1; then
          tail -n 60 "$work/$doc.pass$pass.stdout" >&2
          exit 1
        fi
      done
      cp "$work/$doc.pdf" "$doc.pdf"
      printf 'Built %s/%s.pdf\n' "$lang" "$doc"
    done
  )
done
