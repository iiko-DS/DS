#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает «контактный лист» из блока «На экране» нескольких страниц — для глазной проверки.

Рядом с превью страницы ставится её имя; разметка берётся из data/<slug>.json
(preview_html) и подключаются те же стили, что на самих страницах.

Запуск: python preview-sheet.py <slug> [<slug> ...]
Пишет iiko-ds-mobile/prototypes/recommendations/_sheet.html и печатает путь.
"""
import json
import os
import sys

DS = r"C:\Users\asukharev\GitHub\DS"
REC = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
OUT = os.path.join(DS, "_audit", "rec", "out")
DATA = os.path.join(DS, "_audit", "rec", "data")

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="../../iiko-ds-web/font.css">
<link rel="stylesheet" href="../../iiko-ds-web/tokens.css">
<link rel="stylesheet" href="../../iiko-ds-mobile/modes.css">
<link rel="stylesheet" href="../../iiko-ds-mobile/components/index.css">
<link rel="stylesheet" href="../../iiko-ds-web/styles.css">
<link rel="stylesheet" href="../../iiko-ds-web/components/index.css">
<link rel="stylesheet" href="../../iiko-ds-web/components/Checkbox_DS/checkbox.css">
<link rel="stylesheet" href="../../iiko-ds-web/components/Checkbox_DS/checkbox-icons.css">
<link rel="stylesheet" href="../../iiko-ds-web/components/Radio-Button_DS/radio.css">
<link rel="stylesheet" href="../../iiko-ds-web/components/Radio-Button_DS/radio-icons.css">
<link rel="stylesheet" href="../iiko-ds-mobile/prototypes/recommendations/rec.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
<style>
body{margin:0;padding:12px;background:#eef0f3;font-family:'Roboto','Helvetica Neue',Arial,sans-serif}
.row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:0 0 14px;
     background:#fff;border:1px solid #ddd;border-radius:12px;padding:12px}
h2{font:500 15px/22px 'Roboto','Helvetica Neue',Arial,sans-serif;margin:0 0 8px}
.cell{zoom:0.78}
</style>
</head>
<body>
%(rows)s
</body>
</html>
"""


def main():
    slugs = sys.argv[1:]
    rows = []
    for i in range(0, len(slugs), 2):
        pair = slugs[i:i + 2]
        cells = []
        for slug in pair:
            d = json.load(open(os.path.join(DATA, slug + ".json"), encoding="utf-8"))
            cells.append('<div><h2>%s</h2><div class="cell">%s</div></div>'
                         % (d["component"], d.get("preview_html", "")))
        rows.append('<div class="row">%s</div>' % "".join(cells))
    out = os.path.join(OUT, "_preview-sheet.html")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(TEMPLATE % {"rows": "\n".join(rows)})
    print(out)


if __name__ == "__main__":
    main()
