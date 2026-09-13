"""Shoot every recommendation page (desktop half) and tile them into contact sheets."""
import os, glob, subprocess, shutil, tempfile, math, sys
from PIL import Image, ImageDraw

DS = r"C:\Users\asukharev\GitHub\DS"
OUT = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
CROPS = os.path.join(DS, "_crops", "desk")
SHEETS = os.path.join(DS, "_crops", "sheets")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"
os.makedirs(CROPS, exist_ok=True)
os.makedirs(SHEETS, exist_ok=True)

only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
pages = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(OUT, "*.html"))
               if not os.path.basename(p).startswith(("index", "_")))
if only:
    pages = [p for p in pages if p in only]

tiles = []
for pg in pages:
    png = os.path.join(CROPS, pg + ".png")
    if not os.path.exists(png):
        prof = os.path.join(tempfile.gettempdir(), "udd_sheet")
        shutil.rmtree(prof, ignore_errors=True)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--user-data-dir=" + prof, "--virtual-time-budget=9000",
                        "--window-size=1920,2600", "--screenshot=" + png, BASE + pg + ".html"],
                       capture_output=True, timeout=150)
    im = Image.open(png).convert("RGB")
    im = im.crop((0, 0, 960, im.size[1]))
    # trim trailing white
    g = im.convert("L").point(lambda v: 0 if v > 247 else 255)
    bbox = g.getbbox()
    if bbox:
        im = im.crop((0, 0, im.size[0], min(im.size[1], bbox[3] + 12)))
    tiles.append((pg, im))
    print("tile", pg, im.size)

W = 470
scaled = []
for pg, im in tiles:
    r = W / im.size[0]
    scaled.append((pg, im.resize((W, max(1, int(im.size[1] * r))), Image.LANCZOS)))

per = 4
for i in range(0, len(scaled), per):
    grp = scaled[i:i + per]
    cols = 2
    rows = math.ceil(len(grp) / cols)
    ch = max(t[1].size[1] for t in grp)
    sheet = Image.new("RGB", (W * cols + 12, (ch + 22) * rows + 8), "white")
    d = ImageDraw.Draw(sheet)
    for k, (pg, im) in enumerate(grp):
        cx = (k % cols) * (W + 12)
        cy = (k // cols) * (ch + 22) + 18
        d.text((cx + 4, cy - 14), pg, fill="black")
        sheet.paste(im, (cx, cy))
    name = "sheet_%02d_%s.png" % (i // per + 1, "_".join(t[0] for t in grp)[:60])
    sheet.save(os.path.join(SHEETS, name))
    print("SHEET", name, sheet.size)
