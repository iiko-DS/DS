#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
echo "== tutorials/data mentions =="
grep -o -E '.{70}tutorials/data.{70}' hig_index.js hig_common.js | head -10
echo "== hig mentions =="
grep -o -E '.{50}(hig|human-interface-guidelines).{50}' hig_index.js hig_common.js | head -20
echo "== contentUrl / fetch patterns =="
grep -o -E '.{40}(contentUrl|content_url|fetch\()[^;]{0,120}' hig_index.js hig_common.js | head -20
