# -*- coding: utf-8 -*-
import re, os, sys, json, difflib
RAW = os.path.dirname(os.path.abspath(__file__))
def norm(s):
    for a, b in [("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u2014", "-"), ("\u00a0", " "), ("\u2026", "...")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()

def diag(file, quote):
    t = norm(open(os.path.join(RAW, file), encoding="utf-8", errors="replace").read())
    q = norm(quote)
    if q in t:
        print("OK", file, q[:60]); return
    print("FAIL", file, "|", q[:70])
    anchor = " ".join(q.split()[:6])
    i = t.find(anchor)
    print("  anchor idx:", i)
    if i >= 0:
        win = t[i:i + max(len(q), 40)]
        sm = difflib.SequenceMatcher(None, q, win)
        print("  ratio:", round(sm.ratio(), 3))
        for tag, a1, a2, b1, b2 in sm.get_opcodes():
            if tag != "equal":
                print("   ", tag, "QUOTE:", repr(q[a1:a2])[:120], "SRC:", repr(win[b1:b2])[:120])
