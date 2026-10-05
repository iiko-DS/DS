#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/iiko-DS/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
mkdir -p hig || true
for slug in layout disclosure-controls outline-views lists-and-tables collections cards sidebars; do
  code=$(curl -s -m 40 -A "$UA" -o "hig/$slug.json" -w "%{http_code}" "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/$slug.json")
  echo "$code $slug $(wc -c < hig/$slug.json)"
done
