#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка дописанных паттернов: адреса источников, цитаты, три пункта, дубли.
Только чтение; сравнивает с git-снимком, чтобы смотреть именно новые записи."""
import json
import glob
import os
import re
import subprocess

DS = r"C:\Users\asukharev\GitHub\DS"
PAT = os.path.join(DS, "_audit", "rec", "out", "patterns")

issues = []
total_new = 0
for p in sorted(glob.glob(os.path.join(PAT, "*.json"))):
    slug = os.path.basename(p)[:-5]
    new = json.load(open(p, encoding="utf-8")).get("patterns_ru") or []
    old_raw = subprocess.run(["git", "show", "82fc2ea:_audit/rec/out/patterns/%s.json" % slug],
                             capture_output=True, text=True, cwd=DS).stdout
    old = (json.loads(old_raw).get("patterns_ru") or []) if old_raw.strip() else []
    fresh = new[len(old):]
    total_new += len(fresh)
    titles = [x.get("title") for x in new]
    dup = [t for t in set(titles) if titles.count(t) > 1]
    if dup:
        issues.append("%s: повторяющиеся заголовки: %s" % (slug, dup[:3]))
    for i, x in enumerate(fresh, 1):
        src = str(x.get("src") or "")
        items = x.get("items") or []
        if "https://" not in src and "http://" not in src:
            issues.append("%s: новый паттерн %d «%s» — в источнике нет полного адреса" % (slug, i, x.get("title")))
        if len(items) != 3:
            issues.append("%s: новый паттерн %d — пунктов %d (нужно 3)" % (slug, i, len(items)))
        joined = " ".join(str(v) for v in items)
        if len(items) == 3 and "Что происходит" not in items[0]:
            issues.append("%s: новый паттерн %d — первый пункт не «Что происходит»" % (slug, i))
        if len(items) == 3 and "Что делать нам" not in items[2]:
            issues.append("%s: новый паттерн %d — третий пункт не «Что делать нам»" % (slug, i))
        if not re.search(r"[A-Za-z]{3,}", joined):
            issues.append("%s: новый паттерн %d — нет английской цитаты" % (slug, i))
        if not x.get("example_html") or not x.get("example_ru"):
            issues.append("%s: новый паттерн %d — нет примера или подписи" % (slug, i))
        if any(len(str(v)) < 25 for v in items):
            issues.append("%s: новый паттерн %d — слишком короткий пункт" % (slug, i))

print("новых паттернов проверено:", total_new)
print("замечаний:", len(issues))
for s in issues[:40]:
    print("  -", s)
