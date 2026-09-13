#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

echo "== M3 site path probes =="
for p in components/lists/specs components/cards/specs components/menus/specs foundations/accessibility/accessibility-basics foundations/accessibility/designing foundations/layout/applying-layout components/expansion-panels components/tables components/toolbars; do
  code=$(curl -s -m 30 -A "$UA" -o m3_probe.html -w "%{http_code}" "https://m3.material.io/$p")
  t=$(grep -o -E '<title>[^<]*</title>' m3_probe.html | head -1)
  d=$(grep -o -E '<meta name="description" content="[^"]*"' m3_probe.html | head -1)
  echo "$code | $p | $t | $d"
done

echo "== Apple HIG path probes =="
for p in layout cards disclosure-controls outline-views collections buttons lists-and-tables; do
  code=$(curl -s -m 30 -A "$UA" -o hig_probe.html -w "%{http_code}" "https://developer.apple.com/design/human-interface-guidelines/$p")
  t=$(grep -o -E '<title>[^<]*</title>' hig_probe.html | head -1)
  echo "$code | $p | $t"
done

echo "== material-web internal path probe =="
for p in internal/_touch-target.scss internal/_shared.scss docs/theming/README.md; do
  code=$(curl -s -m 30 -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/material-components/material-web/main/$p")
  echo "$code $p"
done
