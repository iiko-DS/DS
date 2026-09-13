#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Раскладывает отчёты субагентов (JSON из файлов subagent-summary-*.txt) на кандидатов
в паттерны по компонентам: out/new-patterns/<slug>.json и out/new-patterns.md.

Запуск:
    python checks/new-patterns-to-json.py 20260913_04     # маска по дате в имени файла
    python checks/new-patterns-to-json.py                # все свежие (последние 12 файлов)

Ничего в data/*.json не пишет — только заготовки для просмотра."""
import glob
import json
import os
import re
import sys

DS = r"C:\Users\asukharev\GitHub\DS"
CACHE = r"C:\Users\asukharev\AppData\Local\hermes\cache\delegation"
OUT = os.path.join(DS, "_audit", "rec", "out", "new-patterns")


def load_reports(mask=None):
    files = sorted(glob.glob(os.path.join(CACHE, "subagent-summary-*.txt")))
    if mask:
        files = [f for f in files if mask in os.path.basename(f)]
    else:
        files = files[-12:]
    reports = []
    for p in files:
        raw = open(p, encoding="utf-8", errors="replace").read()
        blocks = re.findall(r"```json\s*(.*?)```", raw, re.S) or [raw]
        for b in blocks:
            i, j = b.find("{"), b.rfind("}")
            if i < 0 or j < 0:
                continue
            try:
                data = json.loads(b[i:j + 1])
            except Exception:
                continue
            if data.get("components"):
                reports.append((os.path.basename(p), data))
                break
    return reports


def main():
    mask = sys.argv[1] if len(sys.argv) > 1 else None
    reports = load_reports(mask)
    print("отчётов с JSON:", len(reports))
    os.makedirs(OUT, exist_ok=True)
    total = 0
    md = ["# Кандидаты в паттерны поведения (из сборов)", ""]
    for name, data in reports:
        for c in data.get("components") or []:
            slug = c.get("slug")
            items = c.get("situations") or c.get("items") or []
            if not slug or not items:
                continue
            total += len(items)
            md.append("\n## %s  (%d)" % (slug, len(items)))
            for s in items:
                if not isinstance(s, dict):
                    md.append("- %s" % s)
                    continue
                md.append("- **%s**" % (s.get("situation") or s.get("behavior") or "?"))
                for k, label in (("happens", "Что происходит"), ("systems", "Что делают системы"),
                                 ("us", "Что делать нам")):
                    if s.get(k):
                        md.append("  - %s: %s" % (label, s[k]))
                src = " · ".join(x for x in [s.get("who"), s.get("url")] if x)
                if s.get("quote"):
                    md.append("  - цитата: «%s»" % s["quote"])
                if src:
                    md.append("  - источник: %s%s" % (src, "" if s.get("verified", True) else "  (НЕ ПОДТВЕРЖДЕНО)"))
            json.dump(items, open(os.path.join(OUT, slug + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    open(os.path.join(DS, "_audit", "rec", "out", "new-patterns.md"), "w",
         encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print("ситуаций:", total)
    print("файлы:", OUT)
    print("сводка: %s" % os.path.join(DS, "_audit", "rec", "out", "new-patterns.md"))


if __name__ == "__main__":
    main()
