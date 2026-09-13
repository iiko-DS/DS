#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Desktop-side defect detectors over the DS recommendation pages.

D1 CONTENTBOX  element whose rendered height differs from the height its own CSS
               declares by roughly (padding-top+bottom+border-top+bottom)
               -> a `height: Npx` rule without box-sizing: border-box.
D2 NATIVE      a raw UA form control (input[type=checkbox|radio|range|number])
               that is actually painted -> the DS component CSS is not loaded
               or does not cover the element.
D3 EMPTY       visible styled element that renders 0x0 (invisible marker).
D4 SIZEGAP     element whose rect is smaller than its own declared height
               (overflow/clipping of a fixed-height container).
"""
import os, re, glob, subprocess, shutil, tempfile, sys

DS = r"C:\Users\asukharev\GitHub\DS"
OUT = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"

JS = r"""<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const PAGES = %(pages)s, ONLY = %(mode)s, OUT = []; let i = 0;
function scan(doc, win, page){
  doc.querySelectorAll('.panel').forEach(pan=>{
    const mode = pan.dataset.mode || 'desktop';
    if (ONLY && mode !== ONLY) return;
    const walk = (el) => {
      const c = win.getComputedStyle(el);
      if (c.display==='none' || c.visibility==='hidden' || c.opacity==='0') return;
      const r = el.getBoundingClientRect();
      const cls = ((el.className||'')+'' || el.tagName).slice(0,46);
      const tag = el.tagName.toLowerCase();
      // D2 raw UA control actually painted
      if (tag === 'input') {
        const t = (el.type||'text').toLowerCase();
        if (['checkbox','radio','range'].includes(t) && r.width>0 && r.height>0
            && !el.classList.contains('ds-native-hidden')) {
          OUT.push('NATIVE | '+page+' ['+mode+'] '+tag+'[type='+t+'] | '+Math.round(r.width)+'x'+Math.round(r.height)+' | '+cls);
        }
      }
      // D1 content-box height mismatch on elements that declare a height
      let declH = el.style.height, declW = el.style.width, src = 'inline';
      if (!declH || !/px$/.test(declH)) {
        // look at the element's own matched rules via the CSSStyleSheet
        src = 'css';
        declH = null;
        for (const sh of doc.styleSheets) {
          let rules; try { rules = sh.cssRules; } catch(e) { continue; }
          if (!rules) continue;
          for (const rule of rules) {
            if (!rule.selectorText || !rule.style) continue;
            let m = false;
            try { m = el.matches(rule.selectorText); } catch(e) { continue; }
            if (!m) continue;
            if (rule.style.height && /px$/.test(rule.style.height)) declH = rule.style.height;
          }
        }
      }
      if (declH) {
        const dh = parseFloat(declH);
        const pad = parseFloat(c.paddingTop)+parseFloat(c.paddingBottom)
                  + parseFloat(c.borderTopWidth)+parseFloat(c.borderBottomWidth);
        const box = c.boxSizing;
        const expected = box === 'border-box' ? dh : dh + pad;
        if (pad > 0 && Math.abs(r.height - expected) > 1.5 && Math.abs(r.height - dh) < 0.6) {
          OUT.push('CONTENTBOX | '+page+' ['+mode+'] '+cls+' | declared h='+dh+' rendered '+Math.round(r.height)+' pad+border='+pad+' box-sizing='+box+' ('+src+')');
        }
      }
      [...el.children].forEach(walk);
    };
    walk(pan);
  });
}
function next(){ if (i>=PAGES.length){ document.getElementById('out').textContent = OUT.length?OUT.join(String.fromCharCode(10)):'NONE'; return; }
  const page = PAGES[i++]; const f = document.createElement('iframe');
  f.style.cssText = 'width:1600px;height:1400px;border:0';
  f.src = '/iiko-ds-mobile/prototypes/recommendations/'+page+'.html';
  f.onload = () => setTimeout(()=>{ scan(f.contentDocument, f.contentWindow, page); f.remove(); next(); }, 350);
  document.body.appendChild(f); }
next();
</script></body>"""


def main():
    pages = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(OUT, "*.html"))
                   if not os.path.basename(p).startswith(("index", "_")))
    mode = sys.argv[1] if len(sys.argv) > 1 else "desktop"
    wrapper = os.path.join(OUT, "_desktop_detectors.html")
    prof = os.path.join(tempfile.gettempdir(), "udd_desk")
    shutil.rmtree(prof, ignore_errors=True)
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS % {"pages": repr(pages).replace("'", '"'), "mode": repr(mode)})
    try:
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--virtual-time-budget=150000", "--user-data-dir=" + prof, "--dump-dom",
               BASE + "_desktop_detectors.html"]
        dom = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
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
        print("WARNING: no output -- server up?")
        return 2
    kinds = ["NATIVE", "CONTENTBOX", "EMPTY", "SIZEGAP"]
    for k in kinds:
        found = [l for l in lines if l.startswith(k + " |")]
        print("-- %s: %d" % (k, len(found)))
        for l in found:
            print("     ", l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
