#!/usr/bin/env bash
set -u
cd "$HOME/GitHub/iiko-DS/DS/_audit/platform/_src"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
for u in \
 "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/layout.json" \
 "https://developer.apple.com/design/human-interface-guidelines/layout/index.json" \
 "https://developer.apple.com/design/human-interface-guidelines/layout.json" \
 "https://developer.apple.com/design/human-interface-guidelines/data/layout.json" ; do
  code=$(curl -s -m 30 -A "$UA" -o probe_out.json -w "%{http_code}" "$u")
  echo "$code $(wc -c < probe_out.json) $u"
done
echo "== js bundle search for api path =="
grep -o -E '.{50}index\.json.{50}' hig_index.js hig_common.js | head -5
grep -o -E '.{40}(/tutorials/data|dataUrl|contentPath)[^,;]{0,80}' hig_index.js hig_common.js | head -10
echo "== rowheight json =="
python - <<'PY'
import json
d = json.load(open('ad_rowheight.json', encoding='utf-8'))
def flat(x):
    if isinstance(x, dict):
        if x.get('type') == 'text':
            return x.get('text', '')
        return ''.join(flat(v) for v in x.values())
    if isinstance(x, list):
        return ''.join(flat(v) for v in x)
    return ''
print('TITLE:', d.get('metadata', {}).get('title'))
print('ABSTRACT:', flat(d.get('abstract')))
print('DISCUSSION:', flat(d.get('primaryContentSections'))[:900])
PY
