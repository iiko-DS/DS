#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

echo "== legacy HIG probes =="
for u in \
 "https://developer.apple.com/design/human-interface-guidelines/ios/visual-design/adaptivity-and-layout/" \
 "https://developer.apple.com/design/human-interface-guidelines/foundations/layout/" \
 "https://developer.apple.com/design/human-interface-guidelines/ios/controls/lists-and-tables/" \
 "https://developer.apple.com/design/human-interface-guidelines/components/layout-and-organization/lists-and-tables/" ; do
  code=$(curl -sL -m 40 -A "$UA" -o legacy.html -w "%{http_code}" "$u")
  hits=$(grep -o -i -E ".{60}44 ?(x|×) ?44 ?pt.{60}|.{60}minimum tappable area.{80}" legacy.html | head -2)
  echo "$code $(wc -c < legacy.html) $u"
  [ -n "$hits" ] && echo "   HIT: $hits"
done

echo "== wayback availability =="
curl -s -m 40 "https://archive.org/wayback/available?url=developer.apple.com/design/human-interface-guidelines/layout" ; echo
curl -s -m 40 "https://archive.org/wayback/available?url=developer.apple.com/design/human-interface-guidelines/ios/visual-design/adaptivity-and-layout/" ; echo

echo "== apple search api =="
curl -s -m 40 -A "$UA" "https://developer.apple.com/search/search_data.php?q=minimum%20tappable%20area%2044&results=5" -o apple_search.json -w "%{http_code} %{size_download}\n"
head -c 600 apple_search.json; echo
