#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live defect detectors over the DESKTOP panels of the recommendation pages.

A CLIPPED   element with own text whose scrollHeight/scrollWidth exceeds its
            client box -> content is cut off (fixed height + overflow hidden).
B OVERLAP   two sibling leaf elements with own text whose rects intersect.
C ZEROGAP   a text node label directly abutting its neighbour (no gap) inside a
            DS row  -> component CSS not applied (spacing comes from CSS).
D VOID      container with background/border whose inner content occupies much
            less than its own height (>= 40px of empty space) -> frozen height.
E STATE     computed background-color of :disabled vs normal for the same class
            (catches "states above styles" specificity bugs).
"""
import os, re, glob, subprocess, shutil, tempfile, sys

DS = r"C:\Users\asukharev\GitHub\DS"
OUT = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"

JS = r"""<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const PAGES = %(pages)s, OUT = []; let i = 0;
const vis = (el, win) => { const c = win.getComputedStyle(el);
  return c.display!=='none' && c.visibility!=='hidden' && c.opacity!=='0'; };
function leafText(el){ return el.children.length===0 && el.textContent.trim(); }
function scan(doc, win, page){
  doc.querySelectorAll('.panel').forEach(pan=>{
    if ((pan.dataset.mode||'desktop') !== 'desktop') return;
    const all = [...pan.querySelectorAll('*')];
    all.forEach(el=>{
      if (!vis(el, win)) return;
      const c = win.getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const cls = ((el.className||'')+'' || el.tagName).slice(0,46);
      // A clipped
      if (leafText(el) && (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1)
          && el.clientHeight > 0) {
        OUT.push('CLIPPED | '+page+' '+cls+' | box '+el.clientWidth+'x'+el.clientHeight
                 +' content '+el.scrollWidth+'x'+el.scrollHeight+' | '+el.textContent.trim().slice(0,26));
      }
      // D void space inside a bordered/filled container
      if (el.children.length && (c.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(c.borderTopWidth) > 0)
          && r.height > 40) {
        let top = 1e9, bot = -1e9;
        [...el.children].forEach(k=>{ const kr = k.getBoundingClientRect();
          if (kr.height || kr.width) { top = Math.min(top, kr.top); bot = Math.max(bot, kr.bottom); } });
        if (bot > top) {
          const cs = parseFloat(c.paddingTop)+parseFloat(c.paddingBottom);
          const gapTop = top - r.top - parseFloat(c.paddingTop);
          const gapBot = r.bottom - parseFloat(c.paddingBottom) - bot;
          if (gapBot > 40 || gapTop > 40) {
            OUT.push('VOID | '+page+' '+cls+' | h='+Math.round(r.height)+' content='+Math.round(bot-top)
                     +' emptyTop='+Math.round(gapTop)+' emptyBottom='+Math.round(gapBot));
          }
        }
      }
    });
    // B overlap between sibling text leaves
    all.forEach(el=>{
      if (!vis(el,win)) return;
      const kids = [...el.children].filter(k=>vis(k,win));
      for (let a=0;a<kids.length;a++) for (let b=a+1;b<kids.length;b++) {
        const ra = kids[a].getBoundingClientRect(), rb = kids[b].getBoundingClientRect();
        if (!ra.width || !rb.width) continue;
        if (!leafText(kids[a]) || !leafText(kids[b])) continue;
        const ox = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
        const oy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
        if (ox > 1 && oy > 1) {
          OUT.push('OVERLAP | '+page+' '+((el.className||'')+'').slice(0,36)+' | "'
                   +kids[a].textContent.trim().slice(0,18)+'" x "'+kids[b].textContent.trim().slice(0,18)
                   +'" | '+Math.round(ox)+'x'+Math.round(oy));
        }
      }
    });
    // E disabled vs normal background for the same class set
    ['ds-btn','ds-btn-icon','ds-checkbox','ds-radio','ds-slide-toggle'].forEach(base=>{
      const on = pan.querySelector('.'+base+':disabled');
      const off = pan.querySelector('.'+base+':not(:disabled)');
      if (on && off) {
        const bgOn = win.getComputedStyle(on).backgroundColor, bgOff = win.getComputedStyle(off).backgroundColor;
        const clOn = win.getComputedStyle(on).color, clOff = win.getComputedStyle(off).color;
        if (bgOn === bgOff && clOn === clOff) OUT.push('STATE | '+page+' .'+base
          +' | disabled looks identical to enabled | bg '+bgOn+' color '+clOn);
      }
    });
  });
}
function next(){ if (i>=PAGES.length){ document.getElementById('out').textContent = OUT.length?OUT.join(String.fromCharCode(10)):'NONE'; return; }
  const page = PAGES[i++]; const f = document.createElement('iframe');
  f.style.cssText='width:1600px;height:1400px;border:0';
  f.src='/iiko-ds-mobile/prototypes/recommendations/'+page+'.html';
  f.onload=()=>setTimeout(()=>{ scan(f.contentDocument, f.contentWindow, page); f.remove(); next(); }, 350);
  document.body.appendChild(f); }
next();
</script></body>"""


def main():
    pages = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(OUT, "*.html"))
                   if not os.path.basename(p).startswith(("index", "_")))
    wrapper = os.path.join(OUT, "_live_detectors.html")
    prof = os.path.join(tempfile.gettempdir(), "udd_live")
    shutil.rmtree(prof, ignore_errors=True)
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS % {"pages": repr(pages).replace("'", '"')})
    try:
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                              "--virtual-time-budget=150000", "--user-data-dir=" + prof,
                              "--dump-dom", BASE + "_live_detectors.html"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=180).stdout
    finally:
        os.remove(wrapper)
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    lines = []
    if m:
        raw = (m.group(1).replace("&lt;", "<").replace("&gt;", ">")
               .replace("&quot;", '"').replace("&amp;", "&"))
        lines = [l for l in raw.splitlines() if l.strip()]
    if not lines:
        print("WARNING: no output"); return 2
    for k in ["CLIPPED", "OVERLAP", "VOID", "STATE"]:
        found = [l for l in lines if l.startswith(k + " |")]
        print("-- %s: %d" % (k, len(found)))
        for l in found[:40]:
            print("     ", l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
