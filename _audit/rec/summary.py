#!/usr/bin/env python3
"""Свод по ревью: собирает личные решения в одну таблицу «паттерн × человек».

Читает всё, что лежит в `_audit/rec/review/*.json` (каждый файл — один человек по
одному компоненту), берёт названия паттернов и список правок из `_audit/rec/data/`
и делает страницу `_audit/rec/summary.html`:

  · по каждому компоненту — таблица паттернов, где в столбцах люди, а в клетках
    их решения и комментарии;
  · рядом столбец «Расхождения» — где мнения разошлись (это и есть повестка встречи);
  · по правкам — значения каждого человека и столбец «Итоговое значение»;
  · «Кто ответил» — сколько компонентов прислал каждый человек и кто чего не прислал;
  · столбец «Решение» на встрече заполняется прямо на странице и сохраняется файлом
    `_audit/rec/review/<компонент>.final.json` — ровно тем, который принимает
    `_audit/rec/apply-values.py`.

Запуск:
  python _audit/rec/summary.py                 # собрать страницу
  python _audit/rec/summary.py --open-hint     # то же + подсказка, как открыть
Страница открывается по адресу http://127.0.0.1:8899/_audit/rec/summary.html
(через serve.py, иначе решения со встречи некуда будет сохранить).
"""

import argparse
import glob
import json
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REC = os.path.join(ROOT, "_audit", "rec")
DATA_DIR = os.path.join(REC, "data")
REVIEW_DIR = os.path.join(REC, "review")
OUT = os.path.join(REC, "summary.html")

STATUSES = [("accepted", "check_circle", "Одобряем"), ("later", "schedule", "Отложить"),
            ("rejected", "cancel", "Не подходит")]
ICON = {k: v for k, _, v in [(a, b, c) for a, b, c in STATUSES]}
ICON_NAME = {a: b for a, b, _ in STATUSES}
LABEL = {a: c for a, _, c in STATUSES}
FINAL_PERSON = "final"


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def load_reviews():
    """Все файлы решений: {slug: {person: {...}}} + отдельно итоговые ({slug: {...}})."""
    people, by_component, finals = [], {}, {}
    for path in sorted(glob.glob(os.path.join(REVIEW_DIR, "*.json"))):
        name = os.path.basename(path)[:-5]           # без .json
        if "." not in name:
            continue
        slug, person = name.split(".", 1)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        if person == FINAL_PERSON:
            finals[slug] = data
            continue
        if person not in people:
            people.append(person)
        by_component.setdefault(slug, {})[person] = data
    return people, by_component, finals


def component_data(slug):
    path = os.path.join(DATA_DIR, slug + ".json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def build_model():
    people, by_component, finals = load_reviews()
    model = {"generatedAt": datetime.now().strftime("%d.%m.%Y %H:%M"), "people": people,
             "components": [], "missing": {}, "stats": {}}
    for slug in sorted(set(list(by_component) + list(finals))):
        data = component_data(slug)
        if not data:
            continue
        patterns = []
        for i, g in enumerate(data.get("patterns_ru") or []):
            patterns.append({"id": "pat-%s-%d" % (slug, i), "title": g.get("title") or ("Паттерн %d" % (i + 1))})
        edits = []
        for change in data.get("changes") or []:
            for e in change.get("edit") or []:
                if e.get("id"):
                    edits.append({"id": e["id"], "what": change.get("what") or e["id"],
                                  "desktop": change.get("desktop") or "", "mobile": change.get("mobile") or ""})
        reviews = {p: by_component.get(slug, {}).get(p, {}) for p in people}
        decisions = {p: ((r.get("decisions") or {})) for p, r in reviews.items()}
        values = {p: {k: (v or {}).get("value") for k, v in ((reviews[p].get("edits") or {})).items()} for p in people}

        # где разошлись мнения и где разошлись значения
        split_patterns, split_edits = [], []
        for pat in patterns:
            votes = {decisions[p].get(pat["id"], {}).get("st") for p in people}
            votes.discard(None)
            if len(votes) > 1:
                split_patterns.append(pat["id"])
            pat["votes"] = {p: decisions[p].get(pat["id"], {}) for p in people}
        for edit in edits:
            vals = {values[p].get(edit["id"]) for p in people if values[p].get(edit["id"]) is not None}
            if len(vals) > 1:
                split_edits.append(edit["id"])
            edit["values"] = {p: values[p].get(edit["id"]) for p in people}
        model["components"].append({"slug": slug, "name": data.get("component") or slug,
                                    "patterns": patterns, "edits": edits,
                                    "splitPatterns": split_patterns, "splitEdits": split_edits,
                                    "final": finals.get(slug, {})})
        model["stats"][slug] = {
            "answered": sorted([p for p in people if by_component.get(slug, {}).get(p)]),
            "patterns": len(patterns), "edits": len(edits),
            "split": len(split_patterns) + len(split_edits), "total": len(patterns) + len(edits)}
    for slug in sorted(set([c["slug"] for c in model["components"]])):
        answered = model["stats"][slug]["answered"]
        model["missing"][slug] = [p for p in people if p not in answered]
    return model


def cell(pattern, person, status, label):
    """Клетка паттерна: иконка статуса, комментарий — подсказкой и текстом под ней."""
    if not status:
        return '<td class="c c--empty"></td>'
    note = esc((status.get("note") or "").strip())
    short = ("<div class=\"c__note\">" + (note if len(note) <= 120 else note[:117] + "…") + "</div>") if note else ""
    title = esc(person + ": " + label + ((" — " + note) if note else ""))
    return ('<td class="c c--%s" title="%s"><span class="st"><span class="material-icons">%s</span>%s</span>%s</td>'
            % (status["st"], title, ICON_NAME.get(status["st"], "help"), label, short))


def render(model):
    parts = []
    head = []
    for comp in model["components"]:
        answers = model["stats"][comp["slug"]]
        rows = []
        for pat in comp["patterns"]:
            tds = "".join(cell(pat, p, pat["votes"].get(p) or {}, LABEL.get((pat["votes"].get(p) or {}).get("st"), ""))
                          for p in model["people"])
            flag = '<span class="flag" title="Мнения разошлись">расхождение</span>' if pat["id"] in comp["splitPatterns"] else ""
            rows.append('<tr data-pat="%s" data-split="%s"><td class="w">%s %s</td>%s<td class="fin" data-final-st></td></tr>'
                        % (esc(pat["id"]), "1" if pat["id"] in comp["splitPatterns"] else "0",
                           esc(pat["title"]), flag, tds))
        edit_rows = []
        for edit in comp["edits"]:
            tds = "".join('<td class="v">%s</td>' % (esc(edit["values"].get(p)) if edit["values"].get(p) is not None else "")
                          for p in model["people"])
            flag = '<span class="flag" title="Значения разошлись">расхождение</span>' if edit["id"] in comp["splitEdits"] else ""
            edit_rows.append('<tr data-edit="%s" data-split="%s"><td class="w">%s %s<div class="w__sub">Desktop %s · Mobile %s</div></td>%s'
                             '<td class="fin"><input class="fin__in" type="text" inputmode="decimal" data-final-value '
                             'aria-label="Итоговое значение"></td></tr>'
                             % (esc(edit["id"]), "1" if edit["id"] in comp["splitEdits"] else "0",
                                esc(edit["what"]), flag, esc(edit["desktop"]), esc(edit["mobile"]), tds))
        cols = "".join('<th class="p">%s</th>' % esc(p) for p in model["people"])
        missing = model["missing"].get(comp["slug"]) or []
        note = ('<p class="miss">Не прислали: %s</p>' % esc(", ".join(missing))) if missing else ""
        parts.append("""
<section class="card" data-slug="%(slug)s">
  <div class="card__head" role="button" tabindex="0">
    <h2>%(name)s</h2>
    <span class="badge">%(answered)d из %(people)d ответили · расхождений %(split)d</span>
    <span class="material-icons card__chev">expand_more</span>
  </div>
  <div class="card__body">
    %(miss)s
    <table class="matrix">
      <tr><th class="w">Паттерн</th>%(cols)s<th class="fin">Решение</th></tr>
      %(rows)s
    </table>
    %(edits)s
  </div>
</section>""" % {"slug": esc(comp["slug"]), "name": esc(comp["name"]),
                 "answered": len(answers["answered"]), "people": len(model["people"]),
                 "split": answers["split"], "miss": note, "cols": cols, "rows": "".join(rows),
                 "edits": (('<table class="matrix matrix--edits"><tr><th class="w">Правка</th>' + cols +
                            '<th class="fin">Итоговое значение</th></tr>' + "".join(edit_rows) + "</table>")
                           if edit_rows else "")})

    people_bar = "".join(
        '<span class="who"><b>%s</b> — %d из %d компонентов</span>' % (
            esc(p), sum(1 for c in model["components"] if p in model["stats"][c["slug"]]["answered"]),
            len(model["components"]))
        for p in model["people"]) or '<span class="who">Файлов решений пока нет — присылайте JSON из меню компонентов.</span>'
    data = json.dumps(model, ensure_ascii=False).replace("<", "\\u003c")

    html = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Свод по ревью — Desktop → Mobile</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
<style>
  :root{--stroke:#dde3ec;--muted:#7b8794;--ok:#0f852c;--later:#a35b00;--no:#c62828}
  *{box-sizing:border-box}
  body{margin:0;background:#f5f6f8;font:400 14px/20px 'Roboto','Helvetica Neue',Arial,sans-serif;color:#1b1f24}
  .wrap{max-width:1900px;margin:0 auto;padding:24px}
  h1{font:500 26px/32px 'Roboto',Arial,sans-serif;margin:0 0 4px}
  .sub{color:var(--muted);margin:0 0 16px}
  .tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 16px}
  button{font:500 13px/18px 'Roboto',Arial,sans-serif;padding:7px 12px;border:1px solid var(--stroke);
         background:#fff;border-radius:8px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
  button:hover{background:#f4f5f7}
  button .material-icons{font-size:16px;line-height:1}
  .hint{color:var(--muted);font-size:13px}
  .who{display:inline-block;margin:0 12px 6px 0;padding:4px 10px;background:#fff;border:1px solid var(--stroke);border-radius:999px;font-size:13px}
  .card{background:#fff;border:1px solid var(--stroke);border-radius:12px;margin:0 0 16px;padding:16px 18px}
  .card__head{display:flex;align-items:center;gap:12px;cursor:pointer}
  .card__head h2{font:500 17px/24px 'Roboto',Arial,sans-serif;margin:0}
  .badge{margin-left:auto;color:var(--muted);font-size:13px}
  .card__chev{color:var(--muted);transition:transform .15s ease}
  .card.is-collapsed .card__chev{transform:rotate(-90deg)}
  .card.is-collapsed .card__body{display:none}
  .card__body{margin-top:12px}
  table.matrix{border-collapse:collapse;width:100%;margin:0 0 14px}
  table.matrix th,table.matrix td{border:1px solid var(--stroke);padding:6px 8px;vertical-align:top;text-align:left}
  table.matrix th{background:#f7f9fc;font-weight:500;white-space:nowrap}
  th.w,td.w{width:34%}
  th.p,td.c{width:auto}
  td.c .st{display:inline-flex;align-items:center;gap:4px;font-size:12px;white-space:nowrap}
  td.c .material-icons{font-size:14px;line-height:1}
  td.c--accepted .st{color:var(--ok)} td.c--later .st{color:var(--later)} td.c--rejected .st{color:var(--no)}
  td.c__empty{}
  .c__note{color:#4a5560;font-size:12px;margin-top:3px}
  td.v{font-variant-numeric:tabular-nums}
  td.fin{width:200px;background:#fbfcfe}
  .fin__in{width:90px;padding:4px 6px;border:1px solid var(--stroke);border-radius:6px;font:400 13px/18px 'Roboto',Arial,sans-serif}
  .flag{display:inline-block;margin-left:6px;padding:1px 6px;border-radius:999px;background:#fdecea;color:var(--no);font-size:11px;vertical-align:middle}
  .miss{margin:0 0 10px;color:var(--later);font-size:13px}
  .fin__btns{display:flex;gap:4px}
  .fin__btn{padding:3px 7px;font:500 12px/16px 'Roboto',Arial,sans-serif}
  .fin__btn.is-on[data-st="accepted"]{background:#e7f5eb;border-color:var(--ok);color:var(--ok)}
  .fin__btn.is-on[data-st="later"]{background:#fff4e5;border-color:#ea7806;color:var(--later)}
  .fin__btn.is-on[data-st="rejected"]{background:#fdecea;border-color:var(--no);color:var(--no)}
  .saved{margin-left:10px;color:var(--ok);font-size:13px}
  code{background:#f1f3f6;padding:1px 5px;border-radius:4px}
</style>
</head>
<body>
<div class="wrap">
  <h1>Свод по ревью: Desktop → Mobile</h1>
  <p class="sub">Собрано @@AT@@ · людей: @@PEOPLE@@ · компонентов с решениями: @@COMPS@@.
     Источник — файлы <code>_audit/rec/review/*.json</code>.</p>
  <div class="tools">
    <button type="button" id="save"><span class="material-icons">save</span>Сохранить решения</button>
    <span class="saved" id="saved"></span>
    <button type="button" id="xls"><span class="material-icons">table_view</span>Отчёт xls</button>
    <label class="hint"><input type="checkbox" id="onlySplit"> только расхождения</label>
    <button type="button" id="expandAll"><span class="material-icons">unfold_more</span>Раскрыть всё</button>
    <span class="hint">Решение сохраняется файлом <code>review/&lt;компонент&gt;.final.json</code> —
      его принимает <code>apply-values.py</code>.</span>
  </div>
  <div class="who-bar">@@BAR@@</div>
  @@PARTS@@
</div>
<script id="data" type="application/json">@@DATA@@</script>
<script>
/* Страница свода: столбец «Решение» заполняется на встрече, значения подсказываются
   из присланных файлов, сохранение — тем же сервером, что и у страниц компонентов. */
var DATA = JSON.parse(document.getElementById('data').textContent);
var ST = [['accepted','check_circle','Берём'],['later','schedule','Отложить'],['rejected','cancel','Не берём']];
var finalState = {};
DATA.components.forEach(function (c) {
  var f = c.final || {};
  finalState[c.slug] = { decisions: {}, edits: {} };
  Object.keys(f.decisions || {}).forEach(function (k) { finalState[c.slug].decisions[k] = (f.decisions[k] || {}).st || ''; });
  Object.keys(f.edits || {}).forEach(function (k) { finalState[c.slug].edits[k] = (f.edits[k] || {}).value; });
});
function mostCommon(counts) {
  /* Подсказываем только при явном перевесе: при ничьей лучше пусто — это и есть
     то, что надо решать на встрече. */
  var best = '', n = 0, second = 0;
  Object.keys(counts).forEach(function (v) {
    if (counts[v] > n) { second = n; n = counts[v]; best = v; }
    else if (counts[v] > second) { second = counts[v]; }
  });
  return (n > second && n >= 2) ? best : '';
}
/* «Решение» по паттернам: три кнопки в последнем столбце. Мода присланных мнений —
   подсказка, а не готовый ответ: на встрече жмут осознанно. */
document.querySelectorAll('.card').forEach(function (card) {
  var slug = card.getAttribute('data-slug');
  var st = finalState[slug] || { decisions: {}, edits: {} };
  card.querySelectorAll('tr[data-pat]').forEach(function (tr) {
    var pid = tr.getAttribute('data-pat'), cellTd = tr.querySelector('[data-final-st]');
    if (!cellTd) return;
    var counts = {};
    tr.querySelectorAll('td.c--accepted,td.c--later,td.c--rejected').forEach(function (td) {
      var cls = td.className.match(/c--(accepted|later|rejected)/);
      if (cls) counts[cls[1]] = (counts[cls[1]] || 0) + 1;
    });
    var on = st.decisions[pid] !== undefined ? st.decisions[pid] : mostCommon(counts);
    var html = '<div class="fin__btns">';
    ST.forEach(function (s) {
      html += '<button class="fin__btn' + (on === s[0] ? ' is-on' : '') + '" type="button" data-st="' + s[0] +
        '" data-pat="' + pid + '" title="' + s[2] + '"><span class="material-icons">' + s[1] + '</span>' + s[2] + '</button>';
    });
    cellTd.innerHTML = html + '</div>';
  });
  card.querySelectorAll('tr[data-edit]').forEach(function (tr) {
    var id = tr.getAttribute('data-edit'), input = tr.querySelector('[data-final-value]');
    if (!input) return;
    if (st.edits[id] !== undefined && st.edits[id] !== null) { input.value = st.edits[id]; return; }
    var counts = {};
    tr.querySelectorAll('td.v').forEach(function (td) {
      var v = (td.textContent || '').trim();
      if (v) counts[v] = (counts[v] || 0) + 1;
    });
    input.value = mostCommon(counts);
  });
});
document.addEventListener('click', function (ev) {
  var t = ev.target;
  var card = t.closest('.card');
  if (!card) return;
  var slug = card.getAttribute('data-slug');
  var head = t.closest('.card__head');
  if (head) { card.classList.toggle('is-collapsed'); return; }
  var btn = t.closest('.fin__btn[data-st]');
  if (btn) {
    var pid = btn.getAttribute('data-pat'), st = btn.getAttribute('data-st');
    var stt = finalState[slug] || (finalState[slug] = { decisions: {}, edits: {} });
    stt.decisions[pid] = (stt.decisions[pid] === st) ? '' : st;
    card.querySelectorAll('.fin__btn[data-pat="' + pid + '"]').forEach(function (b) {
      b.classList.toggle('is-on', b.getAttribute('data-st') === stt.decisions[pid]);
    });
  }
});
document.addEventListener('input', function (ev) {
  var input = ev.target;
  if (!input || !input.hasAttribute('data-final-value')) return;
  var card = input.closest('.card'), slug = card.getAttribute('data-slug');
  var tr = input.closest('tr[data-edit]');
  var stt = finalState[slug] || (finalState[slug] = { decisions: {}, edits: {} });
  stt.edits[tr.getAttribute('data-edit')] = input.value;
});
/* Фильтр «только расхождения»: прячем компоненты, где спорить не о чем. */
var onlySplit = document.getElementById('onlySplit');
onlySplit.addEventListener('change', function () {
  var any = false;
  document.querySelectorAll('.card').forEach(function (card) {
    var slug = card.getAttribute('data-slug');
    var info = (DATA.components.filter(function (c) { return c.slug === slug; })[0] || {});
    var split = (info.splitPatterns || []).length + (info.splitEdits || []).length;
    var hide = onlySplit.checked && split === 0;
    card.style.display = hide ? 'none' : '';
    if (!hide) any = true;
    if (onlySplit.checked) card.classList.remove('is-collapsed');
  });
});
document.getElementById('expandAll').addEventListener('click', function () {
  var closed = document.querySelectorAll('.card.is-collapsed').length > 0;
  document.querySelectorAll('.card').forEach(function (c) { c.classList.toggle('is-collapsed', !closed); });
});
/* Сохранение: по файлу на компонент, только с заполненным решением. */
document.getElementById('save').addEventListener('click', function () {
  /* Сохраняем то, что видно в столбце «Решение»: отмеченные статусы и значения в полях.
     Незаполненное не пишем — «пусто» значит «ещё не решили». */
  var saved = document.getElementById('saved'), jobs = [], slugs = [];
  document.querySelectorAll('.card').forEach(function (card) {
    var slug = card.getAttribute('data-slug');
    var decisions = {}, edits = {}, any = false;
    card.querySelectorAll('tr[data-pat] .fin__btn.is-on[data-st]').forEach(function (b) {
      decisions[b.getAttribute('data-pat')] = { st: b.getAttribute('data-st'), note: '' }; any = true;
    });
    card.querySelectorAll('tr[data-edit] [data-final-value]').forEach(function (inp) {
      var v = String(inp.value == null ? '' : inp.value).trim();
      if (v) { edits[inp.closest('tr[data-edit]').getAttribute('data-edit')] = { value: v, at: new Date().toISOString() }; any = true; }
    });
    if (!any) return;
    slugs.push(slug);
    jobs.push(fetch('/__rec-review', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version: 3, round: 1, kind: 'rec-review-final', component: slug,
        componentName: (DATA.components.filter(function (c) { return c.slug === slug; })[0] || {}).name || slug,
        person: 'final', savedAt: new Date().toISOString(), decisions: decisions, seen: {}, edits: edits })
    }).then(function (r) { return r.json(); }));
  });
  if (!jobs.length) { saved.textContent = 'Отметьте решения или впишите значения — тогда и сохраним.'; return; }
  saved.textContent = 'Сохраняю…';
  Promise.all(jobs).then(function (res) {
    var ok = res.filter(function (r) { return r && r.ok; }).length;
    saved.textContent = 'Сохранено компонентов: ' + ok + ' (' + slugs.join(', ') + ')';
  }, function () { saved.textContent = 'Сервер не принял — страница открыта не через serve.py?'; });
});
/* Отчёт для встречи: та же таблица, но плоским листом. */
document.getElementById('xls').addEventListener('click', function () {
  var esc = function (v) { return String(v == null ? '' : v).replace(/&/g, '&amp;').replace(/</g, '&lt;'); };
  var rows = '<tr><th>Компонент</th><th>Что</th><th>Тип</th><th>' + DATA.people.join('</th><th>') + '</th><th>Решение</th></tr>';
  DATA.components.forEach(function (c) {
    var st = finalState[c.slug] || { decisions: {}, edits: {} };
    c.patterns.forEach(function (p) {
      var votes = DATA.people.map(function (person) {
        var v = (p.votes || {})[person] || {};
        return v.st ? ({ accepted: 'Одобряем', later: 'Отложить', rejected: 'Не подходит' })[v.st] + (v.note ? ' — ' + v.note : '') : '';
      });
      var fin = st.decisions[p.id] ? ({ accepted: 'Берём', later: 'Отложить', rejected: 'Не берём' })[st.decisions[p.id]] : '';
      rows += '<tr><td>' + esc(c.name) + '</td><td>' + esc(p.title) + '</td><td>паттерн</td><td>' + votes.join('</td><td>') + '</td><td>' + esc(fin) + '</td></tr>';
    });
    c.edits.forEach(function (e) {
      var vals = DATA.people.map(function (person) { return (e.values || {})[person] == null ? '' : (e.values || {})[person]; });
      var fin = st.edits[e.id] == null ? '' : st.edits[e.id];
      rows += '<tr><td>' + esc(c.name) + '</td><td>' + esc(e.what) + '</td><td>правка</td><td>' + vals.join('</td><td>') + '</td><td>' + esc(fin) + '</td></tr>';
    });
  });
  var html = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" ' +
    'xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="utf-8"><meta name="ProgId" content="Excel.Sheet">' +
    '<style>table{border-collapse:collapse;font-family:Calibri,Arial,sans-serif;font-size:11pt}' +
    'th,td{border:1px solid #c9d1dc;padding:4px 8px;vertical-align:top;text-align:left}th{background:#eef3f9;font-weight:bold}</style>' +
    '</head><body><h2>Свод по ревью Desktop → Mobile · ' + DATA.generatedAt + '</h2><table>' + rows + '</table></body></html>';
  var blob = new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'rec-summary.xls';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000);
});
</script>
</body>
</html>
"""
    return (html.replace("@@AT@@", model["generatedAt"])
                .replace("@@PEOPLE@@", str(len(model["people"])))
                .replace("@@COMPS@@", str(len(model["components"])))
                .replace("@@BAR@@", people_bar)
                .replace("@@PARTS@@", "".join(parts))
                .replace("@@DATA@@", data))


def main():
    ap = argparse.ArgumentParser(description="Свод по ревью: паттерн × человек")
    ap.add_argument("--open-hint", action="store_true", help="подсказать адрес страницы")
    args = ap.parse_args()
    model = build_model()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(model))
    rel = os.path.relpath(OUT, ROOT).replace(os.sep, "/")
    print("Свод: %s" % rel)
    print("Людей: %d · компонентов с решениями: %d" % (len(model["people"]), len(model["components"])))
    for comp in model["components"]:
        st = model["stats"][comp["slug"]]
        miss = model["missing"].get(comp["slug"]) or []
        print("  %-16s ответили %d из %d · строк %d · расхождений %d%s"
              % (comp["name"], len(st["answered"]), len(model["people"]), st["total"], st["split"],
                 (" · не прислали: " + ", ".join(miss)) if miss else ""))
    if args.open_hint:
        print("\nОткрыть: http://127.0.0.1:8899/%s" % rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
