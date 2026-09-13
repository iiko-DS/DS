#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
for p in "tokens/_md-comp-card.scss" "tokens/_md-comp-data-table.scss" "tokens/_md-comp-expansion-panel.scss" "tokens/_md-comp-tree.scss" \
         "tokens/versions/v0_192/_md-comp-card.scss" "tokens/versions/v0_192/_md-comp-data-table.scss" ; do
  out="mw_probe_$(basename $p)"
  code=$(curl -s -m 45 -A "$UA" -o "$out" -w "%{http_code}" "https://raw.githubusercontent.com/material-components/material-web/main/$p")
  echo "$code $p $(wc -c < $out)"
done
echo "== tree/table scss remaining =="
python - <<'PY'
import re
def show(fn, pattern, ctx=1, limit=25):
    print("=====", fn)
    lines = open(fn, encoding="utf-8", errors="replace").read().splitlines()
    rx = re.compile(pattern); shown=0
    for i,l in enumerate(lines):
        if rx.search(l):
            for j in range(max(0,i-ctx), min(len(lines), i+ctx+1)):
                print(f"   {j+1}| {lines[j]}")
            shown+=1
            if shown>=limit: break
show("am_tree_tree.scss", r"min-height|padding|height")
show("am_table_table.scss", r"container-height|padding|font-size|sticky")
show("am_list_list.scss", r"padding|height|72px")
PY
