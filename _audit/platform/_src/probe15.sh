#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
echo "== HIG outline/table phrase check =="
grep -o -E ".{80}outline view instead of a table view.{80}" hig/lists-and-tables.json | head -2
echo "== M3 web docs touch target mention =="
for d in button menu checkbox; do
  curl -s -m 45 -o "mw_docs_$d.md" "https://raw.githubusercontent.com/material-components/material-web/main/docs/components/$d.md"
  echo "--- $d: $(grep -c -E '48 ?(px|dp)' mw_docs_$d.md) hits"
  grep -o -E ".{80}48 ?(px|dp).{80}" mw_docs_$d.md | head -3
done
echo "== card.scss image size block =="
sed -n '185,250p' am_card_card.scss
