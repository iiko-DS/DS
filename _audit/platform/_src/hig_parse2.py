import json, os, re

os.chdir(os.path.expanduser("~/GitHub/DS/_audit/platform/_src/hig"))

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

for slug in ["accessibility", "buttons", "disclosure-controls"]:
    d = json.load(open(slug + ".json", encoding="utf-8"))
    blob = " ".join(flat(d.get("primaryContentSections")))
    print("#########", slug, len(blob))
    for m in re.finditer(r"44|tappable|touch target|Tap target", blob, re.I):
        s = max(0, m.start() - 320)
        print("   >>>", blob[s:m.end() + 320].replace("\n", " "))
        print()
