import json, os, re, sys

os.chdir(os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform/_src/hig"))

def flat(x, out=None):
    if out is None:
        out = []
    if isinstance(x, dict):
        if x.get("type") == "text" and isinstance(x.get("text"), str):
            out.append(x["text"])
        for k, v in x.items():
            if k in ("references", "hierarchy", "seeAlsoSections", "primaryContentSectionsMarkers"):
                continue
            flat(v, out)
    elif isinstance(x, list):
        for v in x:
            flat(v, out)
    return out

KWS = {
    "layout": ["44", "tappable", "touch target", "grouped", "margin", "safe area"],
    "disclosure-controls": ["disclosure", "chevron", "outline", "info button", "expand"],
    "outline-views": ["outline", "hierarch", "disclosure", "indent", "row"],
    "lists-and-tables": ["grouped", "plain", "inset", "44", "row", "style"],
    "collections": ["grid", "card", "row"],
}

for slug, kws in KWS.items():
    fn = slug + ".json"
    d = json.load(open(fn, encoding="utf-8"))
    txt = flat(d.get("primaryContentSections"))
    blob = " ".join(txt)
    print("#########", slug, "chars", len(blob))
    for kw in kws:
        found = False
        for m in re.finditer(re.escape(kw), blob, re.I):
            s = max(0, m.start() - 200)
            print(f"   [{kw}] ...{blob[s:m.end()+240]}...")
            found = True
            break
        if not found:
            print(f"   [{kw}] NOT FOUND")
