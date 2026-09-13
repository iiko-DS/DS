"""Screenshot recommendation pages (headless Chrome) and crop the DESKTOP half."""
import os, subprocess, shutil, sys, tempfile

DS = r"C:\Users\asukharev\GitHub\DS"
OUT = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
CROPS = os.path.join(DS, "_crops")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"
os.makedirs(CROPS, exist_ok=True)

pages = sys.argv[1].split(",") if len(sys.argv) > 1 else ["checkbox", "input-number", "form-field", "button"]
mode = sys.argv[2] if len(sys.argv) > 2 else "desktop"

for pg in pages:
    prof = os.path.join(tempfile.gettempdir(), "udd_shot")
    shutil.rmtree(prof, ignore_errors=True)
    png = os.path.join(CROPS, "_%s_%s.png" % (pg, mode))
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--user-data-dir=" + prof, "--virtual-time-budget=9000",
           "--window-size=1920,3000", "--screenshot=" + png, BASE + pg + ".html"]
    subprocess.run(cmd, capture_output=True, timeout=120)
    try:
        from PIL import Image
        im = Image.open(png)
        w, h = im.size
        box = (0, 0, 960, h) if mode == "desktop" else (960, 0, w, h)
        im.crop(box).save(png)
        print("OK", pg, im.size, "->", os.path.basename(png))
    except Exception as e:
        print("ERR", pg, e)
