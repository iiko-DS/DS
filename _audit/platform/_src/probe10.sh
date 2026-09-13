#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

fetch() { code=$(curl -s -m 60 -A "$UA" -o "$2" -w "%{http_code}" "$1"); echo "$code $2 $(wc -c < "$2")"; }

fetch "https://raw.githubusercontent.com/material-components/material-web/main/tokens/_md-sys-shape.scss" mw_sys_shape.scss
fetch "https://raw.githubusercontent.com/material-components/material-web/main/tokens/_md-sys-state.scss" mw_sys_state.scss
fetch "https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-typescale.scss" mw_typescale.scss
fetch "https://raw.githubusercontent.com/angular/components/main/src/material/button/_m3-button.scss" am_m3_button.scss
fetch "https://m3.material.io/static/angular/main.71b75c898cbb56ee.js" m3_main.js

echo "== m3 main.js api hints =="
grep -o -E 'https://[a-zA-Z0-9.-]+/[a-zA-Z0-9._/-]{0,60}' m3_main.js | sort -u | head -25
echo "== m3 main.js json/endpoint hints =="
grep -o -E '"/[a-zA-Z0-9._/-]{3,60}(json|api)[a-zA-Z0-9._/-]{0,30}"' m3_main.js | sort -u | head -20
grep -o -E '.{40}(contentUrl|content_url|firebasestorage|assets/)[^"'"'"']{0,90}' m3_main.js | head -10
