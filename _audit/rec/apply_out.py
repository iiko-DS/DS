"""Переносит заготовки из _audit/rec/out/{edits,previews,platforms,patterns}/ в data/<slug>.json.

Затем (если запустить с --build) собирает страницы: python build.py.

Зачем: правки приходят готовыми файлами от исполнителей (edits — поля 4-й колонки
«Правка», previews — блок «На экране» из 3 экранов, platforms — колонки
Material / iOS HIG / Логика), а data/*.json — единственный источник страниц.

Формат заготовки:
  out/edits/<slug>.json      {"slug": "...", "edits": [{"row": 0, "edits": [...]}]}
  out/previews/<slug>.json   {"slug": "...", "preview_html": "<div class=\"phones\">…"}
  out/platforms/<slug>.json  {"slug": "...", "platform_notes_ru": [...], "logic_ru": [...]}

Запуск:  python apply_out.py           # записать данные
         python apply_out.py --build   # записать и собрать страницы
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, obj):
    """Данные пишем тем же видом, что и остальные файлы: отступ 1, CRLF."""
    text = json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n"))


def apply_edits(d, patch, report):
    """Строки таблицы: поля правки и — если пришло — новый текст колонки Mobile.

    «то же / та же / те же» в Mobile заменяем на числа из Desktop: значение на
    мобиле то же, но это цифры, а не слово (так просил владелец)."""
    changes = d.get("changes") or []
    n_mobile = 0
    for item in patch.get("edits") or []:
        row = item.get("row")
        if not isinstance(row, int) or not (0 <= row < len(changes)):
            report.append("  ! строка %s вне changes" % row)
            continue
        if item.get("mobile"):
            changes[row]["mobile"] = item["mobile"]
            n_mobile += 1
        if "edits" in item:
            changes[row]["edit"] = item.get("edits") or []
    report.append("  edits: %d строк, Mobile переписан в %d" % (len(patch.get("edits") or []), n_mobile))


def main():
    build = "--build" in sys.argv
    touched = []
    report = []
    for path in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        d = load(path)
        slug = d["slug"]
        report.append(slug)
        changed = False
        for kind, keys in (("edits", ("edits",)),
                           ("previews", ("preview_html",)),
                           ("platforms", ("platform_notes_ru", "logic_ru")),
                           ("patterns", ("patterns_ru",))):
            p = os.path.join(OUT, kind, slug + ".json")
            if not os.path.exists(p):
                continue
            patch = load(p)
            if kind == "edits":
                apply_edits(d, patch, report)
                changed = True
            else:
                for k in keys:
                    if patch.get(k):
                        d[k] = patch[k]
                        changed = True
                        report.append("  %s: %s" % (k, len(patch[k]) if isinstance(patch[k], list) else "html"))
        if changed:
            save(path, d)
            touched.append(slug)
    print("обновлено файлов:", len(touched))
    print("\n".join(report) if len(touched) else "(заготовок не найдено)")
    if build and touched:
        print(subprocess.run([sys.executable, os.path.join(HERE, "build.py")],
                             cwd=HERE, capture_output=True, text=True).stdout)


if __name__ == "__main__":
    main()
