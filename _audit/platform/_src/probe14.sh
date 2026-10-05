#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/iiko-DS/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
echo "== full token file list (t..z + tree/expansion check) =="
grep -o -E "_md-comp-[a-z0-9-]+\.scss" gh_tokens_dir.html | sort -u | tail -25
echo "--- tree/expansion/accordion present? ---"
grep -o -E "_md-comp-[a-z0-9-]+\.scss" gh_tokens_dir.html | sort -u | grep -E "tree|expans|accordion|table" || echo "(none besides data-table)"
echo "== fetch card + data-table token values =="
for p in _md-comp-elevated-card.scss _md-comp-filled-card.scss _md-comp-outlined-card.scss; do
  curl -s -m 45 -A "$UA" -o "mw_$p" "https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/$p"
  echo "--- $p $(wc -c < mw_$p)"
  grep -n -E "padding|size|shape|height|width|font" "mw_$p" | head -25
done
echo "===== data-table ====="
grep -n -E "container-height|outline-width|padding|font|size|space|selected|sort" mw_probe__md-comp-data-table.scss | head -40
