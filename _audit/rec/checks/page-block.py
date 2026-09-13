#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Замер блока на странице рекомендаций: где стоит, сколько занимает, как отображается.

Печатает для каждого селектора (можно несколько через запятую) его класс, координаты,
размер и display, плюс размеры его прямых детей — видно, встал ли блок рядом, а не уехал.

Запуск: python page-block.py <slug> "<селектор>[;<селектор>]"
Пример: python page-block.py checkbox ".editrow;.edits"
"""
import html as _html
import os
import re
import shutil
import subprocess
import sys
import tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"

JS = """<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const SLUG = %(slug)s, SELECTORS = %(sels)s, OUT = [];
const f = document.createElement('iframe');
f.style.cssText = 'width:1500px;height:1200px;border:0';
f.src = '/iiko-ds-mobile/prototypes/recommendations/' + SLUG + '.html';
f.onload = () => setTimeout(()=>{
  const d = f.contentDocument, w = f.contentWindow;
  OUT.push('страница: ' + d.body.scrollHeight + ' px высотой, ширина ' + d.documentElement.clientWidth);
  SELECTORS.forEach(sel => {
    const el = d.querySelector(sel);
    if (!el){ OUT.push('нет элемента: ' + sel); return; }
    const b = el.getBoundingClientRect();
    OUT.push(sel + ' -> ' + (el.className || el.tagName) + ' | x=' + Math.round(b.left)
             + ' y=' + Math.round(b.top) + ' ' + Math.round(b.width) + 'x' + Math.round(b.height)
             + ' | display=' + w.getComputedStyle(el).display);
    [...el.children].forEach(c => {
      const cb = c.getBoundingClientRect();
      const cls = (c.className || c.tagName).toString().slice(0, 34);
      OUT.push('    ' + cls + ' | x=' + Math.round(cb.left) + ' y=' + Math.round(cb.top)
               + ' ' + Math.round(cb.width) + 'x' + Math.round(cb.height));
    });
  });
  document.getElementById('out').textContent = OUT.join(String.fromCharCode(10));
}, 450);
document.body.appendChild(f);
</script></body>"""


def main():
    slug = sys.argv[1]
    sels = (sys.argv[2] if len(sys.argv) > 2 else ".editrow;.edits").split(";")
    wrapper = r"C:\Users\asukharev\GitHub\DS\iiko-ds-mobile\prototypes\recommendations\_page_block.html"
    prof = os.path.join(tempfile.gettempdir(), "udd_block")
    shutil.rmtree(prof, ignore_errors=True)
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS % {"slug": '"%s"' % slug, "sels": repr(sels).replace("'", '"')})
    try:
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                              "--virtual-time-budget=30000", "--user-data-dir=" + prof,
                              "--dump-dom", BASE + "_page_block.html"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=200).stdout
    finally:
        os.remove(wrapper)
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    print(_html.unescape(m.group(1)) if m else "нет вывода")


if __name__ == "__main__":
    main()
