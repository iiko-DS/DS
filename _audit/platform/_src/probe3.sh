#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

curl -s -m 60 -A "$UA" -o hig_common.js "https://developer.apple.com/tutorials/js/chunk-common.233ff197.js"
curl -s -m 60 -A "$UA" -o hig_index.js "https://developer.apple.com/tutorials/js/index.8342ca55.js"
echo "sizes: $(wc -c < hig_common.js) $(wc -c < hig_index.js)"

echo "== grep for data url templates =="
grep -o -E '.{60}(data/|/data|\.json).{60}' hig_index.js | head -20
echo "----"
grep -o -E '.{60}(data/|/data|\.json).{60}' hig_common.js | head -20

echo "== candidate endpoints =="
for u in \
 "https://developer.apple.com/tutorials/data/human-interface-guidelines/layout.json" \
 "https://developer.apple.com/tutorials/data/hig/layout.json" \
 "https://developer.apple.com/design/data/hig/layout.json" \
 "https://developer.apple.com/design/human-interface-guidelines/layout/data.json" \
 "https://developer.apple.com/tutorials/data/documentation/human-interface-guidelines.json" ; do
  code=$(curl -s -m 30 -A "$UA" -o probe_out.json -w "%{http_code}" "$u")
  echo "$code $(wc -c < probe_out.json) $u"
done
