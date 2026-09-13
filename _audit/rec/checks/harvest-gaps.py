#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Разбор отчётов субагентов: вытаскивает JSON и печатает по компонентам,
чего не хватает (missing) и что самое нужное (top). Только чтение."""
import json
import glob
import os
import re
import sys

CACHE = r"C:\Users\asukharev\AppData\Local\hermes\cache\delegation"
files = sorted(glob.glob(os.path.join(CACHE, "subagent-summary-*-20260913_035341_*.txt")))
print("файлов:", len(files))
rows = {}
order = []
for p in files:
    raw = open(p, encoding="utf-8", errors="replace").read()
    # JSON может быть в ```json ... ``` или просто в тексте
    blocks = re.findall(r"```json\s*(.*?)```", raw, re.S)
    blocks = blocks or [raw]
    got = False
    for b in blocks:
        i, j = b.find("{"), b.rfind("}")
        if i < 0 or j < 0:
            continue
        try:
            data = json.loads(b[i:j + 1])
        except Exception:
            continue
        comps = data.get("components") or []
        if not comps:
            continue
        for c in comps:
            slug = c.get("slug")
            if not slug:
                continue
            rows[slug] = c
            if slug not in order:
                order.append(slug)
        got = True
        break
    print(os.path.basename(p), "->", "разобран" if got else "JSON не найден")

print("\nвсего компонентов в отчётах:", len(order))
print(sorted(order))

out = os.path.join(r"C:\Users\asukharev\GitHub\DS\_audit\rec\out", "gaps-review.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("сохранено:", out)

for slug in order:
    c = rows[slug]
    print("\n===", slug)
    for m in c.get("missing") or []:
        if isinstance(m, dict):
            print("   нет:", m.get("concern"), "|", m.get("why"), "|", m.get("where"))
        else:
            print("   нет:", m)
    for t in c.get("top") or []:
        print("   важно:", t)
    for d in c.get("defects") or []:
        print("   дефект:", d)
