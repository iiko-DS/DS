#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/iiko-DS/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
mkdir -p hig
for slug in accessibility buttons gesture-controls images navigation-bars tab-bars toolbars menus lists-and-tables charts essential-features; do
  code=$(curl -s -m 40 -A "$UA" -o "hig/$slug.json" -w "%{http_code}" "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/$slug.json")
  n=$(grep -o -E "44[^0-9]{0,3}(x|×)?[^0-9]{0,3}44|44 points|44pt" "hig/$slug.json" | wc -l)
  echo "$code $slug hits44=$n"
done
