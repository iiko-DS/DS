#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка заготовки по компоненту: превью (2 экрана) и строки с полями «Правка».

Читает, если есть, заготовки:
    out/previews/<slug>.json   {"slug": "...", "preview_html": "<div class=\"phones\">…"}
    out/edits/<slug>.json      {"slug": "...", "edits": [{"row": 0, "mobile": "…", "edits": [ … ]}]}
иначе проверяет то, что уже лежит в data/<slug>.json (режим «уже влито»).

Что проверяет:
  PREV-2SCREEN   превью не из двух экранов;
  PREV-BALANCE   разметка не сходится по div;
  PREV-CLASS     класс, которого нет ни в CSS ДС, ни в rec.css;
  PREV-NOCOMP    главного компонента нет на одном из экранов;
  ROW            строка вне changes;
  STILL-TAKZHE   в Mobile осталось «то же / та же / те же», хотя в Desktop есть числа;
  SEL            селектор поля не встречается в разметке страницы;
  CSS            в поле нет «@» или свойство не похоже на CSS;
  DUP-ID         одинаковые id у двух полей.

Запуск: python check-patch.py <slug> [<slug> ...]
"""
import glob
import json
import os
import re
import sys

DS = r"C:\Users\asukharev\GitHub\DS"
HERE = os.path.join(DS, "_audit", "rec")
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
from mock import check_balance  # noqa: E402

TAKZHE = re.compile(r"\b(то же|та же|тот же|те же|так же|тот же самый)\b", re.I)
NUM = re.compile(r"\d")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}")
SIZE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:px|dp|pt)\b|\d+\s*/\s*\d+|\d+\s*[×x]\s*\d+", re.I)


def has_sizes(text):
    """Есть ли в строке размеры (цифры), а не только цвета и слова."""
    return bool(SIZE.search(HEX.sub(" ", str(text))))
PROPS_OK = set("""height min-height max-height width min-width max-width padding padding-top padding-bottom
padding-left padding-right padding-inline padding-block font-size line-height gap row-gap column-gap
border-radius margin margin-left margin-right margin-top margin-bottom transform top left right bottom
border box-shadow""".split())


def css_classes(paths):
    out = set()
    for p in paths:
        s = open(p, encoding="utf-8", errors="replace").read()
        out |= set(re.findall(r"\.([a-zA-Z][\w-]*)", s))
    return out


def component_classes(ds_page):
    return css_classes(glob.glob(os.path.join(DS, "iiko-ds-web", "components", ds_page, "*.css"))
                       + glob.glob(os.path.join(DS, "iiko-ds-mobile", "components", ds_page, "*.css")))


def known_classes():
    """Классы, которым есть чем рисоваться: CSS ДС, каркас страницы и разметка
    примеров на самих страницах (там штатные классы ДС, которых нет в CSS)."""
    known = css_classes(glob.glob(os.path.join(DS, "iiko-ds-web", "components", "**", "*.css"), recursive=True)
                        + glob.glob(os.path.join(DS, "iiko-ds-mobile", "components", "**", "*.css"), recursive=True)
                        + glob.glob(os.path.join(DS, "iiko-ds-web", "*.css"))
                        + glob.glob(os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations", "*.css")))
    for p in glob.glob(os.path.join(DATA, "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        for ex in d.get("examples") or []:
            for cls in re.findall(r'class="([^"]+)"', ex.get("html", "")):
                known |= set(cls.split())
    return known


def check(slug, known):
    problems = []
    d = json.load(open(os.path.join(DATA, slug + ".json"), encoding="utf-8"))
    pv_path = os.path.join(OUT, "previews", slug + ".json")
    ed_path = os.path.join(OUT, "edits", slug + ".json")
    preview = None
    if os.path.exists(pv_path):
        try:
            preview = json.load(open(pv_path, encoding="utf-8")).get("preview_html")
        except Exception as e:
            problems.append("PREV-JSON | %s | %s" % (slug, e))
    else:
        preview = d.get("preview_html")
    if preview is not None:
        n = preview.count("phones__item")
        if n != 2:
            problems.append("PREV-2SCREEN | %s | экранов %d" % (slug, n))
        bal, err = check_balance(preview)
        if bal != 0 or err:
            problems.append("PREV-BALANCE | %s | %s %s" % (slug, bal, err))
        for cls in re.findall(r'class="([^"]+)"', preview):
            for name in cls.split():
                if name.startswith("ds-") and name not in known:
                    problems.append("PREV-CLASS | %s | %s" % (slug, name))
        own = component_classes(d.get("ds_page", ""))
        parts = re.split(r'(?=<div class="phones__item">)', preview)
        # у последней части в конце стоит ещё закрытие обёртки .phones — снимаем его,
        # иначе «два экрана» никогда не сравняются
        if len(parts) == 3 and parts[2].rstrip().endswith("</div>"):
            parts[2] = parts[2].rstrip()[:-len("</div>")]
        for i, s in enumerate(parts[1:], 1):
            if own and not any(("." + c) and ('class="%s' % c in s or c in s) for c in own):
                problems.append("PREV-NOCOMP | %s | экран %d" % (slug, i))
        # Интерфейс на двух экранах один и тот же: шапка и шторка совпадают.
        if len(parts) == 3:
            s1, s2 = parts[1], parts[2]
            h1 = re.findall(r'phone__title">(.*?)<', s1)
            h2 = re.findall(r'phone__title">(.*?)<', s2)
            if h1 != h2:
                problems.append("PREV-INTERFACE | %s | шапки разные: %s / %s" % (slug, h1, h2))
            n1, n2 = s1.count('class="phone__sheet"'), s2.count('class="phone__sheet"')
            if n1 != n2:
                problems.append("PREV-INTERFACE | %s | шторка не на обоих экранах (%d и %d)" % (slug, n1, n2))
            t1 = re.findall(r'phone__sheet-title">(.*?)<', s1) + re.findall(r'phone__sheet-text">(.*?)<', s1)
            t2 = re.findall(r'phone__sheet-title">(.*?)<', s2) + re.findall(r'phone__sheet-text">(.*?)<', s2)
            if t1 != t2:
                problems.append("PREV-INTERFACE | %s | шторки разные: %s / %s" % (slug, t1, t2))
            # Два экрана — один и тот же интерфейс: вся разметка совпадает, отличаться
            # могут только подписи под экранами (и метка data-preview, её ставит сборка).
            def _one(markup):
                markup = re.sub(r'<p class="phone__caption">.*?</p>', "", markup, flags=re.S)
                return " ".join(markup.split())
            b1, b2 = _one(s1), _one(s2)
            if b1 != b2:
                k = 0
                while k < min(len(b1), len(b2)) and b1[k] == b2[k]:
                    k += 1
                problems.append("PREV-SAME | %s | экраны разные: 1=…%s… 2=…%s…"
                                % (slug, b1[max(0, k - 30):k + 40], b2[max(0, k - 30):k + 40]))

    # паттерны поведения: заготовка или данные
    pt_path = os.path.join(OUT, "patterns", slug + ".json")
    pats = None
    if os.path.exists(pt_path):
        try:
            pats = json.load(open(pt_path, encoding="utf-8")).get("patterns_ru")
        except Exception as e:
            problems.append("PAT-JSON | %s | %s" % (slug, e))
    else:
        pats = d.get("patterns_ru")
    if pats is None:
        problems.append("PAT-MISSING | %s | нет паттернов поведения" % slug)
    else:
        if len(pats) < 3 or len(pats) > 24:
            problems.append("PAT-COUNT | %s | паттернов %d (нужно 3–24: базовые 3–6 плюс дописанные)" % (slug, len(pats)))
        for i, g in enumerate(pats):
            if not g.get("title"):
                problems.append("PAT-TITLE | %s | паттерн %d без заголовка" % (slug, i))
            items = g.get("items") or []
            if len(items) < 2:
                problems.append("PAT-ITEMS | %s | паттерн %d: пунктов %d" % (slug, i, len(items)))
            for it in items:
                if len(str(it)) < 25:
                    problems.append("PAT-SHORT | %s | паттерн %d | слишком короткий пункт: %s" % (slug, i, it))
            if not g.get("src") or "http" not in str(g.get("src", "")) and "(" not in str(g.get("src", "")):
                problems.append("PAT-SRC | %s | паттерн %d | нет строки с источниками" % (slug, i))
            # пример внутри таба: разметка ДС для того же случая + подпись к нему
            ex = g.get("example_html")
            if not ex:
                problems.append("EX-MISSING | %s | паттерн %d | нет примера (example_html)" % (slug, i))
            else:
                if not g.get("example_ru"):
                    problems.append("EX-NOTE | %s | паттерн %d | у примера нет подписи (example_ru)" % (slug, i))
                bal, err = check_balance(ex)
                if bal != 0 or err:
                    problems.append("EX-BALANCE | %s | паттерн %d | %s %s" % (slug, i, bal, err))
                for cls in re.findall(r'class="([^"]+)"', ex):
                    for name in cls.split():
                        if name.startswith("ds-") and name not in known:
                            problems.append("EX-CLASS | %s | паттерн %d | %s" % (slug, i, name))

    # строки: заготовка или данные
    rows = []
    if os.path.exists(ed_path):
        try:
            rows = json.load(open(ed_path, encoding="utf-8")).get("edits") or []
        except Exception as e:
            problems.append("EDIT-JSON | %s | %s" % (slug, e))
    else:
        rows = [{"row": i, "mobile": c.get("mobile"), "edits": c.get("edit")}
                for i, c in enumerate(d.get("changes") or []) if c.get("edit")]
    changes = d.get("changes") or []
    ids = set()
    markup = json.dumps(d, ensure_ascii=False) + (preview or "")
    touched = set()
    for item in rows:
        row = item.get("row")
        if not isinstance(row, int) or not (0 <= row < len(changes)):
            problems.append("ROW | %s | строка %s вне changes" % (slug, row))
            continue
        touched.add(row)
        if item.get("mobile") is not None and not NUM.search(str(item["mobile"])):
            problems.append("MOBILE-NONUM | %s | строка %d | %s" % (slug, row, item["mobile"]))
        for e in item.get("edits") or []:
            sel = e.get("sel", "")
            base = sel.split("::")[0]
            for cls in re.findall(r"\.([\w-]+)", base):
                if cls not in markup:
                    problems.append("SEL | %s | строка %d | селектор не найден: %s" % (slug, row, sel))
            css = e.get("css", "")
            if "@" not in css:
                problems.append("CSS | %s | строка %d | нет @ в %r" % (slug, row, css))
            for p in [x.strip().split(":")[0].strip() for x in css.split(";") if x.strip()]:
                if p not in PROPS_OK:
                    problems.append("CSS | %s | строка %d | свойство %r" % (slug, row, p))
            if e.get("id"):
                if e["id"] in ids:
                    problems.append("DUP-ID | %s | id %s" % (slug, e["id"]))
                ids.add(e["id"])
    # «то же» там, где в Desktop есть числа — должно быть переписано цифрами
    for i, c in enumerate(changes):
        if TAKZHE.search(str(c.get("mobile", ""))) and has_sizes(c.get("desktop", "")):
            if i not in touched:
                problems.append("STILL-TAKZHE | %s | строка %d | Mobile «%s»" % (slug, i, c["mobile"]))
    return problems


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not slugs:
        slugs = [os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(DATA, "*.json")))]
    known = known_classes()
    allp = []
    for slug in slugs:
        allp += check(slug, known)
    print("проверено компонентов: %d · проблем: %d" % (len(slugs), len(allp)))
    for p in allp:
        print("   ", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
