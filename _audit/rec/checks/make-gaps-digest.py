#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Компактная выжимка из out/gaps-review.json: по каждому компоненту — чего не хватает
(без тёмной темы, контраста и локализации — владелец сказал, что это не то) и что
из этого самое нужное. Пишет out/gaps-digest.md. Только чтение данных."""
import json
import os
import re

R = r"C:\Users\asukharev\GitHub\DS\_audit\rec"
data = json.load(open(os.path.join(R, "out", "gaps-review.json"), encoding="utf-8"))

DROP = re.compile(r"контраст|локализ|падеж|перевод|т[её]мн\w*\s+тем|в т[её]мной", re.I)

lines = []
total_missing = 0
for slug in sorted(data):
    c = data[slug]
    miss = [m for m in (c.get("missing") or []) if isinstance(m, dict)]
    keep = [m for m in miss if not DROP.search(str(m.get("concern", "")))]
    dropped = len(miss) - len(keep)
    total_missing += len(keep)
    lines.append("\n## %s" % slug)
    if dropped:
        lines.append("_(отброшено не по теме: %d — тема/контраст/локализация)_" % dropped)
    for m in keep:
        lines.append("- **%s** — %s _(%s)_" % (m.get("concern", "").strip(),
                                               (m.get("why") or "").strip(),
                                               (m.get("where") or "").strip()))
    tops = [t for t in (c.get("top") or []) if not DROP.search(str(t))]
    if tops:
        lines.append("- ▶ важнее всего: " + "; ".join(tops))
    for d in (c.get("defects") or []):
        lines.append("- ⚠ дефект: " + str(d))

head = ("# Чего не хватает в паттернах поведения — выжимка по 38 компонентам\n\n"
        "Источник: разбор 209 паттернов четырьмя проверками (out/gaps-review.json).\n"
        "Вопросы темы, контраста и локализации отсюда убраны — оставлено поведение компонентов.\n"
        "Всего пунктов «чего не хватает»: %d\n" % total_missing)
out = os.path.join(R, "out", "gaps-digest.md")
open(out, "w", encoding="utf-8", newline="\n").write(head + "\n".join(lines) + "\n")
print("пунктов:", total_missing, "| файл:", out)

# короткая сводка по компонентам — по 3 пункта
short = []
for slug in sorted(data):
    c = data[slug]
    keep = [m for m in (c.get("missing") or []) if isinstance(m, dict) and not DROP.search(str(m.get("concern", "")))]
    items = [str(m.get("concern", "")).strip() for m in keep[:3]]
    short.append("%-15s %d | %s" % (slug, len(keep), " · ".join(items)))
print("\n".join(short))
