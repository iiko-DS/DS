#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

for p in layout disclosure-controls outline-views collections lists-and-tables; do
  code=$(curl -s -m 40 -A "$UA" -o "hig_$p.html" -w "%{http_code}" "https://developer.apple.com/design/human-interface-guidelines/$p")
  echo "$code hig_$p.html $(wc -c < hig_$p.html)"
done

echo "== apple docs json probes =="
probe() {
  code=$(curl -s -m 40 -A "$UA" -o "$2" -w "%{http_code}" "$1")
  echo "$code $1 -> $2 $(wc -c < $2)"
}
probe "https://developer.apple.com/tutorials/data/documentation/swiftui/liststyle.json" ad_liststyle.json
probe "https://developer.apple.com/tutorials/data/documentation/uikit/uitableview/style-swift.enum.json" ad_uitableviewstyle.json
probe "https://developer.apple.com/tutorials/data/documentation/uikit/uitableview/rowheight.json" ad_rowheight.json
