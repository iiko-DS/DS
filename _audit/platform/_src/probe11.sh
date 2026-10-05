#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/iiko-DS/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
fetch() { code=$(curl -s -m 60 -A "$UA" -o "$2" -w "%{http_code}" "$1"); echo "$code $2 $(wc -c < "$2")"; }
fetch "https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-shape.scss" mw_shape_vals.scss
fetch "https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-state.scss" mw_state_vals.scss
python - <<'PY'
import re
def show(fn, pattern, ctx=1, limit=25):
    print("=====", fn.replace("_", "-"))
    lines = open(fn, encoding="utf-8", errors="replace").read().splitlines()
    rx = re.compile(pattern); shown=0
    for i,l in enumerate(lines):
        if rx.search(l):
            for j in range(max(0,i-ctx), min(len(lines), i+ctx+1)):
                print(f"   {j+1}| {lines[j]}")
            shown+=1
            if shown>=limit: break
show("mw_shape_vals.scss", r"corner-(medium|large|extra-large|full|none)'")
show("mw_state_vals.scss", r"opacity")
show("am_card_card.scss", r"default-padding|header-size|card-avatar|sm-image|md-image|lg-image|padding: 16px|padding: 8px")
show("am_table_table.scss", r"padding: 0 16px|container-height|font-size")
show("am_tree_tree.scss", r"min-height|padding-left|indent")
PY
