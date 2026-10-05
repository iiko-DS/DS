import json, os, re, urllib.request

SRC = os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform/_src")
os.chdir(SRC)


def flat(x, out=None):
    if out is None:
        out = []
    if isinstance(x, dict):
        if x.get("type") == "text" and isinstance(x.get("text"), str):
            out.append(x["text"])
        for k, v in x.items():
            if k == "hierarchy":
                continue
            flat(v, out)
    elif isinstance(x, list):
        for v in x:
            flat(v, out)
    return out


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def load(path, jsonable=None):
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.endswith(".json"):
        doc = json.loads(raw)
        txt = " ".join(flat(doc))
        raw = txt
    return norm(raw.replace("\u2019", "'"))


# fresh copy of the m3 cards page (meta description quote source)
req = urllib.request.Request("https://m3.material.io/components/cards/specs",
                            headers={"User-Agent": "Mozilla/5.0"})
open("m3_cards.html", "wb").write(urllib.request.urlopen(req, timeout=40).read())
req = urllib.request.Request("https://m3.material.io/components/lists/specs",
                            headers={"User-Agent": "Mozilla/5.0"})
open("m3_lists.html", "wb").write(urllib.request.urlopen(req, timeout=40).read())

CHECKS = [
    ("m3_cards.html", "Cards display content and actions about a single subject. Explore three types: elevated, filled and outlined."),
    ("m3_lists.html", "Lists are continuous, vertical indexes of text and images. Use lists to help users find a specific item and act on it."),
    ("hig/lists-and-tables.json", "the grouped style uses headers, footers, and additional space to separate groups of data"),
    ("hig/lists-and-tables.json", "An info button — called a detail disclosure button when it appears in a list row — doesn't support navigation through a hierarchical table or list."),
    ("hig/lists-and-tables.json", "A disclosure indicator reveals the next level in a hierarchy; it doesn't show details about the item."),
    ("hig/lists-and-tables.json", "Use an outline view instead of a table view to present hierarchical data."),
    ("hig/disclosure-controls.json", "A disclosure triangle shows and hides information and functionality associated with a view or a list of items."),
    ("hig/disclosure-controls.json", "A disclosure triangle points inward from the leading edge when its content is hidden and down when its content is visible."),
    ("hig/outline-views.json", "An outline view includes at least one column that contains primary hierarchical data, such as a set of parent containers and their children."),
    ("hig/outline-views.json", "Parent containers have disclosure triangles that expand to reveal their children."),
    ("ad_uitableviewstyle.json", "A plain table view."),
    ("ad_uitableviewstyle.json", "A table view where sections have distinct groups of rows."),
    ("ad_uitableviewstyle.json", "A table view where the grouped sections are inset with rounded corners."),
    ("ad_liststyle.json", "A protocol that describes the behavior and appearance of a list."),
    ("ad_liststyle.json", "insetGrouped"),
    ("ad_rowheight.json", "The default height in points of each row in the table view."),
    ("am_list_list.md", "the `lines` input has to be set on the `<mat-list-item>`"),
    ("am_list_list.md", 'Uses the `role="listbox"` interaction pattern'),
    ("am_tree_tree.md", "Flat trees are generally easier to style and inspect."),
    ("am_expansion_expansion.md", "imitates the experience of the native `<details>` and `<summary>` elements"),
    ("am_card_card.md", "the standard padding specified in the Material Design spec"),
    ("am_table_table.md", "add a `sticky` input to the `matHeaderRowDef`"),
    ("am_table_table.md", "add the `sticky` or `stickyEnd` directive to the `ng-container` column definition"),
    ("am_table_table.scss", "position: sticky !important;"),
    ("am_card__m3-card.scss", "density: (),"),
    ("mw_probe__md-comp-data-table.scss", "'header-hover-sorting-icon-button-color':"),
    ("mw_probe__md-comp-data-table.scss", "'row-item-selected-container-color':"),
    ("mw_all.ts", "'./list/list-item.js'"),
]

bad = 0
for path, needle in CHECKS:
    hay = load(path)
    n = norm(needle.replace("\u2019", "'"))
    ok = n in hay
    if not ok:
        bad += 1
    print(("OK  " if ok else "FAIL"), path, "|", needle[:70])

# negative checks: claims of absence
print("\n-- absence claims --")
allts = load("mw_all.ts")
for comp in ["card", "expansion", "data-table", "tree"]:
    hit = re.search(r"export \* from '\./%s" % comp, allts)
    print(("FAIL (found!) " if hit else "OK (absent)  "), "material-web all.ts export ./%s" % comp)
m3dir = load("gh_tokens_dir.html")
for name in ["_md-comp-expansion", "_md-comp-tree", "_md-comp-accordion"]:
    print(("FAIL (found!) " if name in m3dir else "OK (absent)  "), "MD3 token file", name)
print("data-table token file present:", "_md-comp-data-table.scss" in m3dir)
print("card token files present:", "_md-comp-elevated-card.scss" in m3dir, "_md-comp-filled-card.scss" in m3dir, "_md-comp-outlined-card.scss" in m3dir)
print("\nFAILURES:", bad)
