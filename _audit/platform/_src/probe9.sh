#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
echo "== m3 slug probes =="
for p in components/tree components/data-table components/table components/accordion components/cards components/lists; do
  code=$(curl -s -m 30 -A "$UA" -o m3_probe.html -w "%{http_code}" "https://m3.material.io/$p")
  t=$(grep -o -E '<title>[^<]*</title>' m3_probe.html | head -1)
  echo "$code $p $t"
done
echo "== m3 html script/api hints =="
grep -o -E '<script[^>]*src="[^"]*"' m3_lists.html | head -10
grep -o -E 'https://[a-zA-Z0-9.-]*(firebaseio|firestore|firebasestorage|contentful|api)[a-zA-Z0-9./_-]*' m3_lists.html | sort -u | head -10
