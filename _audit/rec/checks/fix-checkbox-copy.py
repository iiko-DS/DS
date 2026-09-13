# -*- coding: utf-8 -*-
"""Fix the two page-data files whose text claimed a library fix that the
owner's `git checkout` in iiko-ds-web rolled back (the 4 aggregator imports)."""
import json, io, os

DATA = r"C:\Users\asukharev\GitHub\DS\_audit\rec\data"

FOUND = ("<ul class=\"list\">"
         "<li>Агрегатор <code>iiko-ds-web/components/index.css</code> подключает у Checkbox и Radio только "
         "описания строки (<code>*-label.css</code>). Сами контролы — <code>checkbox.css</code>, "
         "<code>checkbox-icons.css</code>, <code>radio.css</code>, <code>radio-icons.css</code> — не подключает "
         "ни агрегатор, ни одна страница ДС.</li>"
         "<li>Следствие: <code>.ds-checkbox</code> и <code>.ds-radio</code> остаются <code>display:inline</code>, "
         "маркер 20 × 20 не рисуется, цвета состояний не приходят — на экран выходит системный контрол браузера "
         "13 × 13 (замер 12.09.2026: 21 системный контрол на страницах Checkbox, Radio, List).</li>"
         "<li>На этих страницах четыре файла подключены явно из <code>_audit/rec/build.py</code> "
         "(маркер 20 × 20, зазор 8, нативный <code>input</code> скрыт). Собственный CSS компонента библиотеки "
         "верный — не хватало только подключения.</li>"
         "</ul>")

OLD_MARK = "Найдено и починено по ходу"

for slug in ("checkbox", "radio"):
    p = os.path.join(DATA, slug + ".json")
    d = json.load(open(p, encoding="utf-8"))
    r = d["result_html"]
    if OLD_MARK in r:
        # drop the whole <li>…</li> that carries the stale claim
        start = r.find("<li>")
        while start != -1:
            end = r.find("</li>", start)
            frag = r[start:end]
            if OLD_MARK in frag:
                r = r[:start] + r[end + 5:]
                break
            start = r.find("<li>", end)
        d["result_html"] = r
    d["found_html"] = FOUND
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("patched", p, "| stale claim present after:", OLD_MARK in json.load(open(p, encoding="utf-8"))["result_html"])
