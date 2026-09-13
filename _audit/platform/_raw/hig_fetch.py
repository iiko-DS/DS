import json, re, sys, urllib.request, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def inline(items):
    out = []
    for i in items:
        t = i.get("type")
        if t == "text":
            out.append(i.get("text", ""))
        elif t == "codeVoice":
            out.append("`%s`" % i.get("code", ""))
        elif t == "reference":
            out.append(i.get("title") or i.get("identifier", ""))
        elif t == "emphasis" or t == "strong":
            out.append(inline(i.get("inlineContent", [])))
        elif t == "image":
            out.append("[IMAGE]")
        elif t == "link":
            out.append(inline(i.get("inlineContent", [])))
        else:
            if "inlineContent" in i:
                out.append(inline(i["inlineContent"]))
    return "".join(out)

def walk(blocks, depth=0):
    lines = []
    for b in blocks or []:
        t = b.get("type")
        if t == "heading":
            lines.append("#" * b.get("level", 2) + " " + b.get("text", ""))
        elif t == "paragraph":
            lines.append(inline(b.get("inlineContent", [])))
        elif t == "aside":
            lines.append("[" + b.get("style", "aside").upper() + "] " + walk(b.get("content", []), depth))
        elif t == "unorderedList" or t == "orderedList":
            for it in b.get("items", []):
                lines.append("- " + walk(it.get("content", []), depth))
        elif t == "listItem":
            lines.append(walk(b.get("content", []), depth))
        elif t == "codeListing":
            lines.append("```\n" + "\n".join(b.get("code", [])) + "\n```")
        elif t == "table":
            for row in b.get("rows", []):
                cells = []
                for cell in row:
                    cells.append(" ".join(walk(cell, depth)))
                lines.append("| " + " | ".join(cells) + " |")
        elif t == "termList":
            for it in b.get("items", []):
                lines.append("- " + inline(it.get("term", {}).get("inlineContent", [])) + ": " + walk(it.get("definition", {}).get("content", []), depth))
        else:
            if "content" in b:
                lines.append(walk(b["content"], depth))
            elif "inlineContent" in b:
                lines.append(inline(b["inlineContent"]))
    return "\n".join(x for x in lines if x is not None)

def extract(slug):
    url = "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/%s.json" % slug
    d = get(url)
    parts = []
    parts.append("URL: " + "https://developer.apple.com/design/human-interface-guidelines/" + slug)
    meta = d.get("metadata", {})
    parts.append("TITLE: " + str(meta.get("title")))
    parts.append("ABSTRACT: " + inline(d.get("abstract", [])))
    for sec in d.get("primaryContentSections", []) or []:
        if sec.get("kind") == "content":
            parts.append(walk(sec.get("content", [])))
        elif sec.get("kind") == "declarations":
            pass
        else:
            parts.append("[SECTION %s]" % sec.get("kind"))
    for t in d.get("topicSections", []) or []:
        parts.append("TOPIC: " + str(t.get("title")))
    return "\n".join(parts)

if __name__ == "__main__":
    slugs = sys.argv[1:]
    os.makedirs("hig", exist_ok=True)
    for s in slugs:
        try:
            txt = extract(s)
            open("hig/%s.txt" % s, "w", encoding="utf-8").write(txt)
            print("OK %-24s %d chars" % (s, len(txt)))
        except Exception as e:
            print("FAIL %-22s %s" % (s, e))
