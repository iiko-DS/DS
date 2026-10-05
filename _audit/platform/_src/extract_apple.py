import json, re, os, urllib.request

os.chdir(os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform/_src"))

def text_of(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    body = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", body).strip()

for p in ["hig_layout.html", "hig_disclosure-controls.html", "hig_outline-views.html"]:
    t = text_of(p)
    print("#####", p, "textlen", len(t))
    for kw in ["44", "tappable", "touch target", "points", "chevron", "disclosure", "outline"]:
        idx = t.lower().find(kw.lower())
        if idx >= 0:
            print("   ", kw, "->", t[max(0, idx-220):idx+260])
        else:
            print("   ", kw, "-> NOT FOUND")

print("===== HIG json probes =====")
for url in [
    "https://developer.apple.com/tutorials/data/documentation/design/human-interface-guidelines/layout.json",
    "https://developer.apple.com/tutorials/data/documentation/human-interface-guidelines/layout.json",
]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
        print("OK", url, len(data))
        open("hig_layout.json", "wb").write(data)
    except Exception as e:
        print("FAIL", url, e)

for f in ["ad_liststyle.json", "ad_uitableviewstyle.json", "ad_rowheight.json"]:
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("###", f, "parse error", e)
        continue
    print("#####", f)
    print("  title:", d.get("metadata", {}).get("title"))
    print("  abstract:", " ".join(x.get("text", "") for x in d.get("abstract", [])))
    for sec in d.get("topicSections", []) or []:
        print("  section:", sec.get("title"), "->", [i.split("/")[-1] for i in (sec.get("identifiers") or [])])
    for ref, v in list((d.get("references") or {}).items()):
        if v.get("kind") == "symbol" and v.get("role") == "symbol":
            print("   sym:", v.get("title"), "|", " ".join(x.get("text", "") for x in (v.get("abstract") or [])))
