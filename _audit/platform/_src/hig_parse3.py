import json, os, re

os.chdir(os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform/_src/hig"))

def flat(x, out=None):
    if out is None:
        out = []
    if isinstance(x, dict):
        if x.get("type") == "text" and isinstance(x.get("text"), str):
            out.append(x["text"])
        for k, v in x.items():
            if k in ("references", "hierarchy", "seeAlsoSections"):
                continue
            flat(v, out)
    elif isinstance(x, list):
        for v in x:
            flat(v, out)
    return out

for slug, kws in [("lists-and-tables", ["disclosure indicator", "info button", "grouped style", "plain"]),
                  ("disclosure-controls", ["disclosure triangle", "disclosure indicator", "hierarchy", "state"]),
                  ("outline-views", ["disclosure triangles", "hierarch"])]:
    d = json.load(open(slug + ".json", encoding="utf-8"))
    blob = " ".join(flat(d.get("primaryContentSections")))
    print("#########", slug, len(blob))
    for kw in kws:
        m = re.search(re.escape(kw), blob, re.I)
        if m:
            s = max(0, m.start() - 260)
            print(f"   [{kw}]>>>", blob[s:m.end() + 300])
        else:
            print(f"   [{kw}] NOT FOUND")
    print()
