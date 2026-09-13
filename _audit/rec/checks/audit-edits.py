#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка колонки «Правка» на живых страницах рекомендаций.

Для каждого поля .edit__input страницы:
  MISS      селектор поля не находит ни одного элемента в мобильной панели
            или в экранах блока «На экране»;
  NOCHANGE  подставили другое число — измеряемая величина не изменилась,
            значит правка ни на что не влияет и колонка бесполезна;
  SCREENS   в блоке «На экране» не три экрана.

Что измеряем: прямоугольник найденных элементов и вычисленные значения всех
CSS-свойств, которые записывает поле (из data-css, включая шорткаты padding и
margin). Значение подставляется на +8 к исходному, замер берётся через 700 мс —
у части компонентов смена значения идёт с transition, и мгновенный замер врёт.

Дополнительно сверяем страницу с данными: сколько полей и экранов должно быть
по data/<slug>.json и есть ли блок «Что говорят платформы».

Запуск: python audit-edits.py [slug ...] [-v]
"""
import glob
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

DS = r"C:\Users\asukharev\GitHub\DS"
REC = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"

JS = r"""<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const PAGES = %(pages)s, OUT = []; let i = 0;
function flush(){ document.getElementById('out').textContent = OUT.join('\n'); }
function props(css){
  return css.split(';').map(s=>s.trim()).filter(Boolean).map(s=>s.split(':')[0].trim());
}
function measure(win, els, ps, pseudo){
  return els.map(el=>{
    const r = el.getBoundingClientRect(), c = win.getComputedStyle(el, pseudo || null);
    return Math.round(r.width) + 'x' + Math.round(r.height) + '|' +
           ps.map(p=>c.getPropertyValue(p)).join(',');
  }).join(' # ');
}
function scan(doc, win, page, done){
  const fields = [...doc.querySelectorAll('.edit__input')];
  const phones = doc.querySelectorAll('.phones__item').length;
  OUT.push('PAGE | ' + page + ' | полей: ' + fields.length + ' | экранов: ' + phones);
  if (phones !== 2) OUT.push('SCREENS | ' + page + ' | экранов ' + phones + ' вместо 2');
  const rec = [];
  fields.forEach((f, n)=>{
    const raw = f.getAttribute('data-sel'), css = f.getAttribute('data-css') || '';
    const pseudo = raw.indexOf('::') >= 0 ? raw.slice(raw.indexOf('::')) : '';
    const sel = raw.replace(/::[a-z-]+/, '');
    const ps = props(css);
    const targets = [...doc.querySelectorAll('[data-preview="edit"] ' + sel)];
    const deflt = [...doc.querySelectorAll('.phone__screen[data-mode="mobile"]:not([data-preview="edit"]) ' + sel)];
    const id = f.getAttribute('data-id') || n;
    if (!targets.length){ OUT.push('MISS | ' + page + ' | поле ' + id + ' | ' + sel); return; }
    const before = measure(win, targets, ps, pseudo);
    const beforeDefault = measure(win, deflt, ps, pseudo);
    const old = f.value;
    f.value = String(parseFloat(old) + 8);
    f.dispatchEvent(new win.Event('input', {bubbles: true}));
    rec.push({f: f, old: old, sel: raw, ps: ps, pseudo: pseudo, before: before,
              targets: targets, deflt: deflt, beforeDefault: beforeDefault, id: id, now: f.value});
  });
  setTimeout(()=>{
    rec.forEach(r=>{
      const after = measure(win, r.targets, r.ps, r.pseudo);
      if (after === r.before)
        OUT.push('NOCHANGE | ' + page + ' | поле ' + r.id + ' | ' + r.sel
                 + ' | ' + r.now + ' px ничего не изменил');
      if (measure(win, r.deflt, r.ps, r.pseudo) !== r.beforeDefault)
        OUT.push('LEAK | ' + page + ' | поле ' + r.id + ' меняет и первый экран (он должен остаться дефолтным)');
      r.f.value = r.old;
      r.f.dispatchEvent(new win.Event('input', {bubbles: true}));
    });
    done();
  }, 700);
}
function next(){
  if (i >= PAGES.length){ flush(); return; }
  const page = PAGES[i++]; const f = document.createElement('iframe');
  f.style.cssText = 'width:1600px;height:1200px;border:0';
  f.src = '/iiko-ds-mobile/prototypes/recommendations/' + page + '.html';
  f.onload = () => setTimeout(()=>{
    try { scan(f.contentDocument, f.contentWindow, page, ()=>{ f.remove(); flush(); next(); }); }
    catch(e){ OUT.push('ERR | ' + page + ' | ' + e.message); f.remove(); flush(); next(); }
  }, 350);
  document.body.appendChild(f);
}
next();
</script></body>"""


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    pages = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(REC, "*.html"))
                   if not os.path.basename(p).startswith(("index", "_")))
    if want:
        pages = [p for p in pages if p in want]
    wrapper = os.path.join(REC, "_live_edits.html")
    prof = os.path.join(tempfile.gettempdir(), "udd_edits")
    shutil.rmtree(prof, ignore_errors=True)
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS % {"pages": repr(pages).replace("'", '"')})
    try:
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                              "--virtual-time-budget=240000", "--user-data-dir=" + prof,
                              "--dump-dom", BASE + "_live_edits.html"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=400).stdout
    finally:
        os.remove(wrapper)
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    if not m:
        print("WARNING: нет вывода — страница не отрисовалась")
        return 2
    raw = _html.unescape(m.group(1))
    lines = [l for l in raw.splitlines() if l.strip()]
    pages_lines = [l for l in lines if l.startswith("PAGE |")]
    bad = [l for l in lines if not l.startswith("PAGE |")]
    nofields = [l for l in pages_lines if "полей: 0" in l]
    print("страниц: %d · страниц без полей: %d" % (len(pages_lines), len(nofields)))
    # Сверка с данными: сколько полей и экранов должно быть по data/<slug>.json.
    DATA = os.path.join(DS, "_audit", "rec", "data")
    diff = []
    for l in pages_lines:
        slug = l.split("|")[1].strip()
        got_f = int(re.search(r"полей: (\d+)", l).group(1))
        got_s = int(re.search(r"экранов: (\d+)", l).group(1))
        d = json.load(open(os.path.join(DATA, slug + ".json"), encoding="utf-8"))
        want_f = sum(len(c.get("edit") or []) for c in (d.get("changes") or []))
        want_s = (d.get("preview_html") or "").count("phones__item")
        if got_f != want_f:
            diff.append("FIELDS | %s | на странице %d, в данных %d" % (slug, got_f, want_f))
        if got_s != want_s:
            diff.append("PHONES | %s | на странице %d, в данных %d" % (slug, got_s, want_s))
        if not d.get("platform_notes_ru") and not d.get("logic_ru"):
            diff.append("PLATS  | %s | блока «Что говорят платформы» нет" % slug)
    for k in ("SCREENS", "MISS", "NOCHANGE", "LEAK", "ERR"):
        found = [l for l in bad if l.startswith(k + " |")]
        print("-- %s: %d" % (k, len(found)))
        for l in found[:40]:
            print("     ", l)
    print("-- расхождения с данными: %d" % len(diff))
    for l in diff[:60]:
        print("     ", l)
    if "-v" in sys.argv:
        for l in pages_lines:
            print("     ", l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
