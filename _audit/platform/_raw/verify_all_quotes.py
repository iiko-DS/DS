# -*- coding: utf-8 -*-
"""Independent check: every 'quote' in the 5 output JSONs must appear verbatim in the cached source file."""
import json, os, re, glob

RAW = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(RAW)
MW = "https://raw.githubusercontent.com/material-components/material-web/main/"
NG = "https://raw.githubusercontent.com/angular/components/main/src/material/"
HIG = "https://developer.apple.com/design/human-interface-guidelines/"

MAP = {
 MW + "tokens/versions/v0_192/_md-comp-primary-navigation-tab.scss": "val__md-comp-primary-navigation-tab.scss",
 MW + "tokens/versions/v0_192/_md-comp-secondary-navigation-tab.scss": "val__md-comp-secondary-navigation-tab.scss",
 MW + "tokens/versions/v0_192/_md-comp-navigation-bar.scss": "val__md-comp-navigation-bar.scss",
 MW + "tokens/versions/v0_192/_md-comp-navigation-drawer.scss": "val__md-comp-navigation-drawer.scss",
 MW + "tokens/versions/v0_192/_md-comp-snackbar.scss": "val__md-comp-snackbar.scss",
 MW + "tokens/versions/v0_192/_md-comp-list.scss": "val__md-comp-list.scss",
 MW + "tokens/versions/v0_192/_md-comp-menu.scss": "val__md-comp-menu.scss",
 MW + "tokens/versions/v0_192/_md-sys-shape.scss": "shape_v0192.scss",
 MW + "tokens/_md-comp-secondary-tab.scss": "md3tok__md-comp-secondary-tab.scss",
 MW + "tokens/_md-comp-menu.scss": "md3tok__md-comp-menu.scss",
 MW + "menu/internal/_menu.scss": "md3_menu_internal.scss",
 MW + "menu/internal/menuitem/_menu-item.scss": "md3_menuitem.scss",
 MW + "button/internal/_touch-target.scss": "md3_touch_target.scss",
 MW + "labs/navigationbar/internal/_navigation-bar.scss": "md3_navbar_internal.scss",
 MW + "docs/components/tabs.md": "md3_tabs.md",
 MW + "docs/components/menu.md": "md3_menu.md",
 NG + "tabs/_m3-tabs.scss": "ng_tabs__m3-tabs.scss",
 NG + "tabs/_tabs-common.scss": "ng_tabs__tabs-common.scss",
 NG + "tabs/tabs.md": "ng_tabs_tabs.md",
 NG + "tabs/tab-group.ts": "ng_tabs_tab-group.ts",
 NG + "menu/menu.scss": "ng_menu_menu.scss",
 NG + "menu/_m3-menu.scss": "ng_menu__m3-menu.scss",
 NG + "menu/menu.md": "ng_menu_menu.md",
 NG + "core/style/_menu-common.scss": "ng_menu-common.scss",
 NG + "sidenav/sidenav.md": "ng_sidenav_sidenav.md",
 NG + "sidenav/_m3-sidenav.scss": "ng_sidenav__m3-sidenav.scss",
 NG + "sidenav/drawer.scss": "ng_sidenav_drawer.scss",
 NG + "stepper/stepper.md": "ng_stepper_stepper.md",
 NG + "stepper/_stepper-variables.scss": "ng_stepper__stepper-variables.scss",
 NG + "stepper/_m3-stepper.scss": "ng_stepper__m3-stepper.scss",
 NG + "snack-bar/snack-bar.md": "ng_snack-bar_snack-bar.md",
 NG + "snack-bar/snack-bar-container.scss": "ng_snack-bar_snack-bar-container.scss",
 NG + "snack-bar/snack-bar-config.ts": "ng_snack-bar_snack-bar-config.ts",
 NG + "snack-bar/_m3-snack-bar.scss": "ng_snack-bar__m3-snack-bar.scss",
}

def norm(s):
    for a, b in [("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u2014", "-"), ("\u00a0", " "), ("\u2026", "...")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()

def source_text(url):
    if url in MAP:
        return open(os.path.join(RAW, MAP[url]), encoding="utf-8", errors="replace").read()
    if url.startswith(HIG):
        slug = url[len(HIG):].strip("/")
        p = os.path.join(RAW, "higjson", slug + ".json")
        if os.path.exists(p):
            return json.dumps(json.load(open(p, encoding="utf-8")), ensure_ascii=False)
        p2 = os.path.join(RAW, "hig", slug + ".txt")
        if os.path.exists(p2):
            return open(p2, encoding="utf-8", errors="replace").read()
    return None

def walk_quotes(obj, path=""):
    if isinstance(obj, dict):
        if "quote" in obj and isinstance(obj["quote"], str):
            yield path, obj.get("name", ""), obj["quote"], obj.get("source", "")
        for k, v in obj.items():
            yield from walk_quotes(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_quotes(v, path + "[%d]" % i)

total = ok = skipped = 0
bad = []
for slug in ["tabs", "menu", "sidenav", "stepper", "snackbar"]:
    d = json.load(open(os.path.join(OUT, slug + ".json"), encoding="utf-8"))
    for path, name, quote, src in walk_quotes(d):
        total += 1
        if quote == "не найдено" or not src or quote.startswith("/"):
            skipped += 1
            continue
        t = source_text(src)
        if t is None:
            bad.append(("NO_SOURCE_CACHE", slug, name, src))
            continue
        if norm(quote) in norm(t):
            ok += 1
        else:
            bad.append(("NOT_VERBATIM", slug, name, src, quote[:80]))

print("total quote fields: %d | verbatim-verified: %d | skipped (не найдено / no quote): %d" % (total, ok, skipped))
print("PROBLEMS:", len(bad))
for b in bad:
    print("  ", b)
