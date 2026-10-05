import json, os, re, urllib.request

SRC = os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform/_src")
OUT = os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform")
os.chdir(SRC)

# make sure the last cited file exists
try:
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/angular/components/main/src/material/table/_table-flex-styles.scss",
        "am_table__table-flex-styles.scss")
    print("fetched _table-flex-styles.scss OK", os.path.getsize("am_table__table-flex-styles.scss"))
except Exception as e:
    print("fetch flex styles FAILED", e)

MW_MAP = {
    "_md-comp-list.scss": "mw_probe__md-comp-list.scss",
    "_md-comp-list-item.scss": "mw_tokens__md-comp-list-item.scss",
    "_list.scss": "mw_list_internal__list.scss",
    "_md-comp-data-table.scss": "mw_probe__md-comp-data-table.scss",
    "_md-comp-elevated-card.scss": "mw__md-comp-elevated-card.scss",
    "_md-comp-filled-card.scss": "mw__md-comp-filled-card.scss",
    "_md-comp-outlined-card.scss": "mw__md-comp-outlined-card.scss",
    "_md-sys-shape.scss": "mw_shape_vals.scss",
    "_md-sys-state.scss": "mw_state_vals.scss",
    "_md-sys-typescale.scss": "mw_typescale.scss",
    "all.ts": "mw_all.ts",
}
HIG_MAP = {
    "lists-and-tables": "hig/lists-and-tables.json",
    "accessibility": "hig/accessibility.json",
    "disclosure-controls": "hig/disclosure-controls.json",
    "outline-views": "hig/outline-views.json",
    "collections": "hig/collections.json",
}
APL_MAP = {
    "swiftui/liststyle": "ad_liststyle.json",
    "uikit/uitableview/style-swift.enum": "ad_uitableviewstyle.json",
    "uikit/uitableview/rowheight": "ad_rowheight.json",
}


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


def local_path(url):
    if url is None or "HTTP 404" in url:
        return None
    if "material-web/main/" in url:
        base = url.split("/main/", 1)[1].split("?")[0]
        if "_list.scss" in url and "internal" in url:
            return MW_MAP["_list.scss"]
        return MW_MAP.get(os.path.basename(base))
    if "angular/components/main/" in url:
        rel = url.split("/main/", 1)[1]
        if rel == "src/cdk/tree/padding.ts":
            return "cdk_tree_padding.ts"
        rel = rel.replace("src/material/", "").replace("src/", "")
        name = "am_" + rel.replace("/", "_")
        return name if os.path.exists(name) else None
    if "tutorials/data/design/human-interface-guidelines/" in url:
        slug = url.rsplit("/", 1)[1].replace(".json", "")
        return HIG_MAP.get(slug)
    if url.rstrip("/").endswith(tuple(HIG_MAP)):
        slug = url.rstrip("/").rsplit("/", 1)[1]
        return HIG_MAP.get(slug)
    if "developer.apple.com/documentation/" in url:
        rel = url.split("/documentation/", 1)[1]
        return APL_MAP.get(rel)
    return None


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def check_quote(quote, path):
    if path is None:
        return None
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.endswith(".json"):
        doc = json.loads(raw)
        raw = " ".join(flat(doc.get("primaryContentSections")) + flat(doc.get("abstract")))
        raw = raw.replace("\u2019", "'")
    hay = norm(raw)
    lines = [norm(l) for l in quote.split("\n")]
    lines = [l for l in lines if l and not l.startswith("//")]
    if not lines:
        return None
    bad = [l for l in lines if l not in hay]
    return bad


problems = []
counts = {}
for slug in ["list", "card", "expansion-panel", "table", "tree"]:
    data = json.load(open(os.path.join(OUT, slug + ".json"), encoding="utf-8"))
    n_entries = n_ok = n_nf = 0
    for plat, block in data["platforms"].items():
        entries = list(block.get("sizes", [])) + list(block.get("states", []))
        for e in entries:
            q = e.get("quote")
            v = e.get("value")
            if q is None or v == "не найдено":
                n_nf += 1
                continue
            n_entries += 1
            path = local_path(e.get("source"))
            if path is None:
                problems.append((slug, plat, e["name"], "NO LOCAL MIRROR for " + str(e.get("source"))))
                continue
            bad = check_quote(q, path)
            if bad is None:
                problems.append((slug, plat, e["name"], "EMPTY QUOTE CHECK"))
            elif bad:
                problems.append((slug, plat, e["name"], "NOT FOUND: " + " | ".join(b[:80] for b in bad)))
            else:
                n_ok += 1
    counts[slug] = (n_entries, n_ok, n_nf)

print("\n==== verification summary (checked/ok/not-found-entries) ====")
for slug, (a, b, c) in counts.items():
    print(f"  {slug}: checked={a} ok={b} 'не найдено'={c}")
print("\n==== problems ====")
for p in problems:
    print("  ", p[0], "/", p[1], "|", p[2], "->", p[3][:220])
print("\nTOTAL problems:", len(problems))
