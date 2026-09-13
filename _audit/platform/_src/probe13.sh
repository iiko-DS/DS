#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
curl -s -m 60 -A "$UA" -o gh_tokens_dir.html "https://github.com/material-components/material-web/tree/main/tokens/versions/v0_192"
echo "dir html bytes: $(wc -c < gh_tokens_dir.html)"
grep -o -E "_md-comp-[a-z0-9-]+\.scss" gh_tokens_dir.html | sort -u
echo "== data-table tokens =="
curl -s -m 45 -A "$UA" -o mw_probe__md-comp-data-table.scss "https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-comp-data-table.scss"
grep -n -E "'[a-z0-9-]*': *(if\(\\\$exclude|map\.get)|container-height|outline-width|padding|font|size|divider" mw_probe__md-comp-data-table.scss | head -60
