#!/usr/bin/env python3
"""Переносит утверждённые значения из файла ревью в мобильный CSS компонента.

Что читает
----------
  · файл решений ревью — `_audit/rec/review/<компонент>.<человек>.json`
    (поле `edits`: {"<id>": {"value": "<число>", "at": "<время>"}});
  · данные компонента — `_audit/rec/data/<slug>.json`, где у каждой правки
    колонки «Что меняется на мобиле» уже лежит машинное описание:
    `id`, `sel` (селектор), `css` (шаблон вида `min-height:@px`) и, если есть,
    `sync` {field, a, b} — линейная связь с соседним полем
    («высота = 2 × паддинг + 20» и обратно).

Что делает
----------
  Собирает из этого правила вида `[data-mode="mobile"] <sel> { … }`, кладёт их
  в файл `iiko-ds-mobile/components/<Папка>_DS/mobile-values.css` и подключает
  его последней строкой в агрегаторе `iiko-ds-mobile/components/index.css`.
  Ничего другого не трогает: ни библиотеку `iiko-ds-web`, ни ручные файлы слоя.

  По умолчанию НИЧЕГО НЕ ПИШЕТ — показывает план и diff. Запись — с `--apply`,
  тогда же печатается команда отката.

Запуск
------
  python _audit/rec/apply-values.py button.Аня.json              # показать diff
  python _audit/rec/apply-values.py button.Аня.json --apply      # записать
  python _audit/rec/apply-values.py путь/к/итог.json --apply     # любой файл той же формы

Итоговые значения (после встречи) удобно положить в такой же файл — например
`_audit/rec/review/button.final.json` с полем `edits` — и запустить так же.
"""

import argparse
import difflib
import glob
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(ROOT, "_audit", "rec", "data")
REVIEW_DIR = os.path.join(ROOT, "_audit", "rec", "review")
MOB_COMPONENTS = os.path.join(ROOT, "iiko-ds-mobile", "components")
INDEX_CSS = os.path.join(MOB_COMPONENTS, "index.css")

VALUES_FILE = "mobile-values.css"          # файл, который собирает этот скрипт
IMPORT_MARK = "значения, утверждённые на ревью"


def slugify(folder):
    """Имя папки компонента → slug: `Form-Field-Input_DS` → `form-field-input`."""
    return re.sub(r"[^a-z0-9]+", "-", folder.replace("_DS", "").lower()).strip("-")


def folders_by_slug():
    out = {}
    for path in glob.glob(os.path.join(MOB_COMPONENTS, "*_DS")):
        if os.path.isdir(path):
            out[slugify(os.path.basename(path))] = os.path.basename(path)
    return out


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_review_file(name):
    if os.path.exists(name):
        return name
    candidate = os.path.join(REVIEW_DIR, name)
    if os.path.exists(candidate):
        return candidate
    return None


def flatten_edits(data):
    """Правки компонента: id → {what, sel, css, sync}."""
    out = {}
    for change in data.get("changes") or []:
        for edit in change.get("edit") or []:
            eid = edit.get("id")
            if not eid:
                continue
            out[eid] = {
                "what": change.get("what") or eid,
                "sel": edit.get("sel") or "",
                "css": edit.get("css") or "",
                "sync": edit.get("sync") or None,
                "default": edit.get("v"),
            }
    return out


def number(value):
    """Значение из файла ревью → число. Пустое или нечисловое — None."""
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        num = float(text)
    except ValueError:
        return None
    return int(num) if float(num).is_integer() else num


def render_declarations(template, value):
    """`min-height:@px` + 48 → `min-height: 48px` (несколько объявлений — через ;)."""
    parts = []
    for chunk in template.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts.append(chunk.replace("@", str(value)))
    return parts


def collect(slug, review, data, warn):
    """Что утверждено → {селектор: [(селектор, [объявления], откуда)]} + отчёт."""
    edits = flatten_edits(data)
    decided = {}
    for eid, item in (review.get("edits") or {}).items():
        if eid not in edits:
            warn("в файле ревью есть правка «%s», которой нет в данных компонента — пропускаю" % eid)
            continue
        value = number((item or {}).get("value"))
        if value is None:
            warn("у правки «%s» значение «%s» не число — пропускаю" % (eid, (item or {}).get("value")))
            continue
        decided[eid] = value

    # Связанное поле: пересчитываем по формуле из данных, если его не задали явно.
    for eid, value in list(decided.items()):
        sync = edits[eid].get("sync")
        if not sync:
            continue
        field = sync.get("field")
        if not field or field in decided or field not in edits:
            continue
        a, b = sync.get("a"), sync.get("b")
        if a is None or b is None:
            continue
        computed = round(a * value + b, 2)
        computed = int(computed) if float(computed).is_integer() else computed
        decided[field] = computed
        warn(None, "%s = %s → %s = %s (формула синхронизации)" % (eid, value, field, computed))

    rules, lines = {}, []
    for eid, value in decided.items():
        edit = edits[eid]
        if not edit["sel"] or not edit["css"]:
            warn("у правки «%s» нет селектора или шаблона — пропускаю" % eid)
            continue
        rules.setdefault(edit["sel"], [])
        for decl in render_declarations(edit["css"], value):
            if decl not in rules[edit["sel"]]:
                rules[edit["sel"]].append(decl)
        lines.append((edit["what"], "; ".join(render_declarations(edit["css"], value)), value, edit["sel"]))
    return rules, lines


def selector_known(slug, selector, folder):
    """Есть ли селектор в CSS компонента (или в общих правилах слоя и режима)."""
    needle = selector.strip().split("::")[0].split(":")[0]
    sources = [os.path.join(MOB_COMPONENTS, "index.css"),
               os.path.join(ROOT, "iiko-ds-mobile", "modes.css"),
               os.path.join(ROOT, "iiko-ds-mobile", "components", "box-sizing.css")]
    sources += glob.glob(os.path.join(MOB_COMPONENTS, folder, "*.css")) if folder else []
    sources += glob.glob(os.path.join(ROOT, "iiko-ds-web", "components", "*_DS", "*.css"))
    for path in sources:
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                if needle and needle in f.read():
                    return True
        except OSError:
            continue
    return False


def build_values_css(component, meta, rules, lines, review_file):
    header = [
        "/* ============================================================",
        "   %s — мобильные значения, утверждённые на ревью" % component,
        "   ============================================================",
        "",
        "   Файл собран скриптом _audit/rec/apply-values.py — руками не правится,",
        "   при следующем запуске будет перезаписан.",
        "",
        "   Источник:  %s%s" % (os.path.relpath(review_file, ROOT).replace(os.sep, "/"),
                              (" — " + meta.get("person", "")) if meta.get("person") else ""),
        "   Собрано:   %s" % datetime.now().strftime("%d.%m.%Y %H:%M"),
        "",
        "   Что утверждено",
        "   --------------",
    ]
    for what, decls, value, sel in lines:
        header.append("     %-28s %-34s (%s)" % (what, decls, sel))
    header += ["   ============================================================ */", ""]

    body = []
    for sel, decls in rules.items():
        body.append('[data-mode="mobile"] %s {\n%s\n}' % (sel, "\n".join("  %s;" % d for d in decls)))
        body.append("")
    return "\n".join(header + body).rstrip() + "\n"


def render_diff(before, after, label):
    diff = list(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                     fromfile=label + " (сейчас)", tofile=label + " (будет)", n=2))
    return "".join(diff) if diff else ""


def main():
    ap = argparse.ArgumentParser(description="Утверждённые значения ревью → мобильный CSS компонента")
    ap.add_argument("review", help="файл решений (например button.Аня.json) или путь к нему")
    ap.add_argument("--apply", action="store_true", help="записать файл значений и подключить его в агрегаторе")
    ap.add_argument("--allow-missing-selector", action="store_true",
                    help="не предупреждать, если селектора нет в CSS компонента")
    args = ap.parse_args()

    warnings = []

    def warn(one_off, note=None):
        if one_off:
            warnings.append("  · " + one_off)
        elif note:
            warnings.append("  · " + note)

    path = find_review_file(args.review)
    if not path:
        print("Не нашёл файл решений: %s" % args.review)
        print("Ищу в: %s" % REVIEW_DIR)
        return 2

    review = load_json(path)
    slug = review.get("component")
    if not slug:
        print("В файле %s нет поля component — не знаю, к какому компоненту он относится." % path)
        return 2

    data_path = os.path.join(DATA_DIR, slug + ".json")
    if not os.path.exists(data_path):
        print("Нет данных компонента: %s" % data_path)
        return 2
    data = load_json(data_path)

    folders = folders_by_slug()
    folder = folders.get(slug)
    if not folder:
        print("Не нашёл папку компонента для «%s» в %s" % (slug, MOB_COMPONENTS))
        return 2

    rules, lines = collect(slug, review, data, warn)
    if not rules:
        print("В файле %s нет утверждённых значений правок — переносить нечего." % os.path.basename(path))
        return 0

    component = data.get("component") or slug
    values_path = os.path.join(MOB_COMPONENTS, folder, VALUES_FILE)
    rel_values = os.path.relpath(values_path, ROOT).replace(os.sep, "/")
    before = open(values_path, encoding="utf-8").read() if os.path.exists(values_path) else ""
    after = build_values_css(component, review, rules, lines, path)

    # Агрегатор: строку подключения ставим последней, чтобы значения перекрывали
    # собственные правила слоя (одна и та же специфичность — решает порядок).
    index_before = open(INDEX_CSS, encoding="utf-8").read()
    import_line = '@import "%s/%s";' % (folder, VALUES_FILE)
    index_after = index_before
    if import_line not in index_after:
        block = "\n/* %s */\n%s\n" % (IMPORT_MARK, import_line)
        index_after = index_after.rstrip("\n") + "\n" + block

    print("Компонент: %s (%s)" % (component, slug))
    print("Файл решений: %s%s" % (os.path.relpath(path, ROOT).replace(os.sep, "/"),
                                  (" — " + str(review.get("person"))) if review.get("person") else ""))
    print("Значения: %s" % rel_values)
    print()
    print("Что уйдёт в CSS:")
    for what, decls, value, sel in lines:
        print("  %-30s %-38s →  %s" % (what, decls, sel))
    print()

    if not args.allow_missing_selector:
        for sel in rules:
            if not selector_known(slug, sel, folder):
                warnings.append("  · селектор %s не найден в CSS компонента — проверь глазами" % sel)

    diff_values = render_diff(before, after, rel_values)
    diff_index = render_diff(index_before, index_after, "iiko-ds-mobile/components/index.css")

    if diff_values:
        print(diff_values)
    else:
        print("Значения уже такие — файл не изменится.")
    if diff_index:
        print(diff_index)

    if warnings:
        print("Замечания:")
        print("\n".join(warnings))
        print()

    if not args.apply:
        print("Это предпросмотр: ничего не записано. Записать — добавь --apply")
        return 0

    os.makedirs(os.path.dirname(values_path), exist_ok=True)
    with open(values_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(after)
    if index_after != index_before:
        with open(INDEX_CSS, "w", encoding="utf-8", newline="\n") as f:
            f.write(index_after)
    print("Записано.")
    print("Откат: git checkout -- iiko-ds-mobile/components/index.css && rm -f %s" % rel_values)
    return 0


if __name__ == "__main__":
    sys.exit(main())
