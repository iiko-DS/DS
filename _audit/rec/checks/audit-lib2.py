import re, glob, os, collections

WEB = r"C:\Users\asukharev\GitHub\DS\iiko-ds-web"
os.chdir(WEB)
def rd(p): return open(p, encoding="utf-8", errors="replace").read()

RULE = re.compile(r'([^{}]+)\{([^{}]*)\}', re.S)

plates, nowrap, contentbox, states_order = [], [], [], []
for p in sorted(glob.glob("components/**/*.css", recursive=True)):
    rel = p.replace(os.sep, "/")
    txt = rd(p)
    for m in RULE.finditer(txt):
        sel = " ".join(m.group(1).split())
        body = m.group(2)
        decls = dict()
        for d in body.split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                decls[k.strip().lower()] = v.strip()
        color = decls.get("color")
        bg = decls.get("background-color") or decls.get("background")
        if color and bg and bg == color and bg.startswith("var("):
            plates.append((rel, sel, bg))
        if "nowrap" in decls.get("white-space", ""):
            nowrap.append((rel, sel))
        if "height" in decls and re.match(r'^\d+(\.\d+)?px$', decls["height"]):
            pad = any(k in decls for k in ("padding", "padding-top", "padding-bottom"))
            bord = any(k in decls for k in ("border", "border-top", "border-bottom", "border-width"))
            bs = decls.get("box-sizing", "")
            if (pad or bord) and bs != "border-box":
                contentbox.append((rel, sel, decls["height"], bs or "-", "pad" if pad else "", "border" if bord else ""))

print("=== PLATES (background == color, same var) : %d ===" % len(plates))
for r, s, v in plates:
    print("   %-52s %-46s %s" % (r.replace("components/", ""), s[:46], v))
print()
print("=== NOWRAP rules: %d ===" % len(nowrap))
for r, s in nowrap[:40]:
    print("   %-52s %s" % (r.replace("components/", ""), s[:60]))
print()
print("=== height:Npx without box-sizing, with padding/border: %d ===" % len(contentbox))
for r, s, h, bs, p, b in contentbox:
    print("   %-52s %-46s h=%-6s box=%-8s %s %s" % (r.replace("components/", ""), s[:46], h, bs, p, b))
