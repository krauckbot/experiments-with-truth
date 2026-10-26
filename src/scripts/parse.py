import re, json, sys, html

src = sys.argv[1]
out = sys.argv[2]
lines = open(src, encoding="utf-8").read().split("\n")

def clean_inline(t):
    t = re.sub(r'<a href="#endnotes[^"]*"[^>]*>.*?</a>', '', t)          # note refs
    t = re.sub(r'<abbr[^>]*>(.*?)</abbr>', r'\1', t)
    t = re.sub(r'<time[^>]*>(.*?)</time>', r'\1', t)
    t = re.sub(r'<(?!/?(em|strong|i|b)\b)[^>]+>', '', t)                 # drop other tags
    t = t.replace('\\\n', '\n')
    t = html.escape(t, quote=False).replace('&lt;', '<').replace('&gt;', '>')
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\s+\\$', '', t)
    return t.strip()

chapters = []
part = None
cur = None
i = 0
mode = None
STOP = {"Endnotes", "Colophon", "Uncopyright", "Imprint"}
skip = True
while i < len(lines):
    L = lines[i]
    m2 = re.match(r'^## (.+)$', L)
    m3 = re.match(r'^### ([IVXLC]+)\s*$', L)
    if m2:
        name = m2.group(1).strip()
        if name in STOP:
            skip = True; cur = None
        elif name.startswith("Part "):
            skip = False; part = name; cur = None
        else:  # Translator's Preface, Introduction, Farewell
            skip = False
            part = {"Translator’s Preface": "Front matter", "Introduction": "Front matter", "Farewell": "Farewell"}.get(name, name)
            cur = {"part": part, "roman": "", "title": name, "paras": []}
            chapters.append(cur)
        i += 1; continue
    if m3 and not skip:
        roman = m3.group(1)
        # title is next non-empty line
        j = i + 1
        while not lines[j].strip(): j += 1
        title = clean_inline(lines[j])
        cur = {"part": part, "roman": roman, "title": title, "paras": []}
        chapters.append(cur)
        i = j + 1; continue
    if skip or cur is None:
        i += 1; continue
    s = L.strip()
    if not s or s.startswith("<div") or s.startswith("</div") or s.startswith("<hgroup") or s.startswith("</hgroup") \
       or s.startswith("<footer") or s.startswith("</footer") or s.startswith("<img") or s.startswith("<figure") or s.startswith("</figure"):
        i += 1; continue
    # gather paragraph (consecutive non-empty lines)
    block = []
    while i < len(lines) and lines[i].strip() and not re.match(r'^#{2,3} ', lines[i]) and not lines[i].strip().startswith(("<div", "</div", "<footer", "</footer", "<hgroup")):
        block.append(lines[i]); i += 1
    if block and block[0].lstrip().startswith(">"):
        verse = [clean_inline(re.sub(r'^\s*>\s?', '', b)) for b in block]
        verse = [v for v in verse if v]
        cur["paras"].append({"t": "q", "h": "<br>".join(verse)})
    else:
        txt = " ".join(b.rstrip().rstrip("\\").strip() for b in block) if not any(b.rstrip().endswith("\\") for b in block) \
            else "<br>".join(clean_inline(b) for b in block)
        h = clean_inline(txt) if "<br>" not in txt else txt
        if h and h not in ("* * *",):
            cur["paras"].append({"t": "p", "h": h})

# drop translator's preface? keep it but mark
for n, c in enumerate(chapters):
    c["id"] = n
print(len(chapters), "sections")
for c in chapters[:3] + chapters[-3:]:
    print(c["id"], c["part"], c["roman"], c["title"], len(c["paras"]))
json.dump(chapters, open(out, "w", encoding="utf-8"), ensure_ascii=False)
