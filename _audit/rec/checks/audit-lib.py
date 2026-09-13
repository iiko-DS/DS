import re, os, glob, collections, sys, json

WEB = r"C:\Users\asukharev\GitHub\DS\iiko-ds-web"
os.chdir(WEB)

def rd(p):
    return open(p, encoding="utf-8", errors="replace").read()

# ---------- 1. aggregator imports ----------
agg = rd("components/index.css")
imps = re.findall(r'@import\s+(?:url\()?["\']([^"\']+)["\']', agg)
missing = [i for i in imps if not os.path.exists(os.path.normpath(os.path.join("components", i)))]
disk = set()
for p in glob.glob("components/**/*.css", recursive=True):
    rel = os.path.relpath(p, "components").replace(os.sep, "/")
    if rel != "index.css":
        disk.add(rel)
imp_norm = set(os.path.normpath(i).replace(os.sep, "/") for i in imps)
print("IMPORTS:", len(imps), "| files on disk:", len(disk))
print("MISSING IMPORT TARGETS:", missing)
print("FILES NOT IMPORTED:", sorted(disk - imp_norm))
print("IMPORTED BUT ABSENT:", sorted(imp_norm - disk))
print()

# ---------- 2. undefined / cross-checked tokens ----------
defined = collections.defaultdict(set)
for f in ("tokens.css", "styles.css"):
    if os.path.exists(f):
        for m in re.finditer(r'(--[A-Za-z0-9_-]+)\s*:', rd(f)):
            defined[m.group(1)].add(f)
print("TOKENS DEFINED:", len(defined))

used = collections.Counter(); loc = collections.defaultdict(set)
for p in glob.glob("components/**/*.css", recursive=True):
    txt = rd(p)
    for m in re.finditer(r'var\(\s*(--[A-Za-z0-9_-]+)', txt):
        used[m.group(1)] += 1
        loc[m.group(1)].add(p.replace(os.sep, "/"))
undef = {k: v for k, v in used.items() if k not in defined}
print("UNDEFINED VAR REFS:", len(undef), "| distinct refs total:", len(used))
for k, v in sorted(undef.items(), key=lambda x: -x[1])[:60]:
    print("   %-60s x%-3d %s" % (k, v, sorted(loc[k])[:2]))
print("TOTAL undefined occurrences:", sum(undef.values()))
