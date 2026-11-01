"""
mirror_pdf.py: build the English translation by editing the ORIGINAL page in place.

The original page is kept as is (logos, colors, boxes, lines, backgrounds, page size). Only the text is
replaced: each original text block is painted out with its own background color and the English text is
written at the same position, in the same size, color, weight and (closest) font.

Three steps:
  1) python3 mirror_pdf.py extract source.pdf blocks.json      -> every text block with position, font, size, color
  2) write translations.json: {"p0b3": "English text", "p0b7": {"text": "...", "sub": "(~ $12.34)", "align": "right"}, ...}
  3) python3 mirror_pdf.py apply source.pdf translations.json translated.pdf [--blocks blocks.json]

Blocks you leave out of translations.json are untouched (use that for numbers, names, codes). `apply` prints
every untouched block that still contains letters so nothing is forgotten by accident, and warns about text
that had to shrink more than 25% or that collides with a neighbor.

Scanned or photographed pages have no text layer: run `ocr` to make a searchable twin first (see SKILL.md).
"""
import json, re, sys, os, collections
import pymupdf

FD = "/usr/share/fonts/truetype/"
FONTS = {  # family -> (regular, bold, italic, bolditalic)
    "sans":  [FD + "liberation/LiberationSans-%s.ttf" % s for s in ("Regular", "Bold", "Italic", "BoldItalic")],
    "serif": [FD + "liberation/LiberationSerif-%s.ttf" % s for s in ("Regular", "Bold", "Italic", "BoldItalic")],
    "mono":  [FD + "liberation/LiberationMono-%s.ttf" % s for s in ("Regular", "Bold", "Italic", "BoldItalic")],
    "wide":  [FD + "dejavu/DejaVuSans%s.ttf" % s for s in ("", "-Bold", "-Oblique", "-BoldOblique")],  # Verdana/Tahoma widths
}


def family_for(fontname):
    n = fontname.lower()
    if re.search(r"verdana|tahoma|dejavu|segoe|trebuchet|lucida", n): return "wide"
    if re.search(r"courier|mono|consol", n): return "mono"
    if re.search(r"times|serif(?!.*sans)|georgia|garamond|cambria|palatino|bookman|minion|baskerville|didot|century", n) and "sans" not in n: return "serif"
    return "sans"


def style_index(fontname, flags):
    n = fontname.lower()
    bold = bool(flags & 16) or "bold" in n or "black" in n or "heavy" in n or "semibold" in n
    ital = bool(flags & 2) or "italic" in n or "oblique" in n
    return (1 if bold else 0) + (2 if ital else 0) if not (bold and ital) else 3


def rgb(c):
    return ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)


def _segments(line):
    """Split one text line into cells: spans separated by a wide horizontal gap are different cells."""
    spans = sorted([sp for sp in line["spans"] if sp["text"].strip()], key=lambda sp: sp["bbox"][0])
    segs = []
    for sp in spans:
        if segs and sp["bbox"][0] - segs[-1][-1]["bbox"][2] <= max(sp["size"] * 1.0, 5) and (abs(sp["size"] - segs[-1][-1]["size"]) < 0.6 or "GlyphLess" in sp["font"]): segs[-1].append(sp)
        else: segs.append([sp])
    return segs


def _is_bold(sp):
    n = sp["font"].lower(); return bool(sp["flags"] & 16) or "bold" in n or "black" in n or "heavy" in n


def _hit(a, b, tol=1.5):
    i = a & b
    return (not i.is_empty) and i.width > tol and i.height > tol


def _color_far(a, b, tol=40):
    return any(abs(((a >> sh) & 255) - ((b >> sh) & 255)) > tol for sh in (16, 8, 0))


def _marked(spans, base):
    """Text of one line, with **bold** and {#rrggbb|colored} markup where a span differs from the block's dominant style."""
    out = []
    for sp in spans:
        t = sp["text"]
        if not t.strip(): out.append(t); continue
        t = t.replace("\u00a0", " ")
        if _is_bold(sp) and not base["bold"]: t = "**" + t + "**"
        if _color_far(sp["color"], base["color"]): t = "{#%06x|%s}" % (sp["color"], t)
        out.append(t)
    return "".join(out)


def _unit(uid, pno, parts):
    """parts: list of span-lists (one per line). Build one block record."""
    chars = collections.Counter(); lines = []; x0 = y0 = 1e9; x1 = y1 = -1e9; xs0 = []; xs1 = []
    for spans in parts:
        for sp in spans:
            chars[(sp["font"], round(sp["size"], 1), sp["color"], sp["flags"])] += len(sp["text"].strip())
            b = sp["bbox"]; x0 = min(x0, b[0]); y0 = min(y0, b[1]); x1 = max(x1, b[2]); y1 = max(y1, b[3])
        xs0.append(min(sp["bbox"][0] for sp in spans)); xs1.append(max(sp["bbox"][2] for sp in spans))
    (font, size, color, flags), _ = chars.most_common(1)[0]
    base = {"bold": all(_is_bold(sp) for spans in parts for sp in spans if sp["text"].strip()), "color": color}   # mixed block: regular base, bold spans get **markup**
    lines = [_marked(spans, base) for spans in parts]
    plain = ["".join(sp["text"] for sp in spans) for spans in parts]
    bases = [spans[0]["origin"][1] for spans in parts]
    pitch = round((bases[-1] - bases[0]) / (len(bases) - 1), 2) if len(bases) > 1 else round(size * 1.2, 2)
    align = "left"
    if len(parts) > 1:
        if max(xs1) - min(xs1) < 2 and max(xs0) - min(xs0) > 4: align = "right"
        elif abs((max(xs0) + max(xs1)) / 2 - (min(xs0) + min(xs1)) / 2) < 2 and max(xs0) - min(xs0) > 4: align = "center"
    elif re.match(r"^[\s\-+()R$\u20ac\u00a3%\d.,/:\u2022*]+$", plain[0]): align = "right"   # numbers/dates: right edge stays anchored
    return {"id": uid, "page": pno, "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)], "text": " ".join(lines),
            "plain": " ".join(plain), "baseline": round(bases[0], 2), "pitch": pitch, "nlines": len(parts),
            "font": font, "size": size, "color": color, "flags": flags, "align": align}


def extract(src, out_json):
    doc = pymupdf.open(src); out = []
    for pno, page in enumerate(doc):
        for bi, b in enumerate(page.get_text("dict")["blocks"]):
            if b["type"] != 0: continue
            lsegs = [_segments(l) for l in b["lines"]]; lsegs = [s for s in lsegs if s]
            if not lsegs: continue
            if all(len(s) == 1 for s in lsegs):   # a paragraph: keep its lines together so the sentence reads naturally
                groups = [[lsegs[0][0]]]
                right = max(ln[0][-1]["bbox"][2] for ln in lsegs); left = min(ln[0][0]["bbox"][0] for ln in lsegs)
                for s in lsegs[1:]:
                    prev = groups[-1][-1]; cur = s[0]
                    # a continuation line: same left edge and size, tight spacing, and the line above ran (nearly) to the right edge
                    same = abs(cur[0]["bbox"][0] - prev[0]["bbox"][0]) < 40 and abs(cur[0]["size"] - prev[0]["size"]) < 0.6 \
                        and cur[0]["bbox"][1] - prev[0]["bbox"][3] < 0.7 * cur[0]["size"] \
                        and prev[-1]["bbox"][2] >= right - 0.12 * max(right - left, 1) and len(groups[-1]) < 40
                    if same: groups[-1].append(cur)
                    else: groups.append([cur])
                for gi, g in enumerate(groups): out.append(_unit(f"p{pno}b{bi}" + (f"g{gi}" if len(groups) > 1 else ""), pno, g))
            else:                                  # table-like row: one block per cell
                for li, segs in enumerate(lsegs):
                    for si, sg in enumerate(segs): out.append(_unit(f"p{pno}b{bi}l{li}s{si}", pno, [sg]))
    for u in out:   # single-line cells: infer right/center alignment from neighbors that share an edge
        if u["nlines"] != 1 or u["align"] != "left": continue
        peers = [v for v in out if v["page"] == u["page"] and v is not u and v["nlines"] == 1]
        same_l = [v for v in peers if abs(v["bbox"][0] - u["bbox"][0]) < 1.0]
        same_r = [v for v in peers if abs(v["bbox"][2] - u["bbox"][2]) < 1.0 and abs(v["bbox"][0] - u["bbox"][0]) > 4]
        same_c = [v for v in peers if abs((v["bbox"][0] + v["bbox"][2]) / 2 - (u["bbox"][0] + u["bbox"][2]) / 2) < 1.0 and abs(v["bbox"][0] - u["bbox"][0]) > 4]
        if same_r and not same_l: u["align"] = "right"
        elif same_c and not same_l and not same_r: u["align"] = "center"
    for u in out:
        if "GlyphLess" in u["font"]:
            pg = doc[u["page"]]; r = pymupdf.Rect(u["bbox"]) & pg.rect
            if r.is_empty: continue
            pix = pg.get_pixmap(clip=r, dpi=150, alpha=False); px = [tuple(pix.samples[i:i + 3]) for i in range(0, len(pix.samples), pix.n)]
            px.sort(key=sum); dark = px[:max(1, len(px) // 12)]
            u["color"] = (sum(p[0] for p in dark) // len(dark)) << 16 | (sum(p[1] for p in dark) // len(dark)) << 8 | (sum(p[2] for p in dark) // len(dark))
            u["scan"] = True
    json.dump(out, open(out_json, "w"), ensure_ascii=False, indent=1)
    print(f"{len(out)} text blocks -> {out_json}")


def bg_color(page, rect):
    """Most common color in a thin ring just outside the block (the block's own background)."""
    pad = 2; r = pymupdf.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad) & page.rect
    pix = page.get_pixmap(clip=r, dpi=144, alpha=False)
    w, h, n = pix.width, pix.height, pix.n; s = pix.samples; cnt = collections.Counter()
    ring = 3
    for y in range(h):
        for x in range(w):
            if x < ring or y < ring or x >= w - ring or y >= h - ring:
                i = (y * w + x) * n; cnt[(s[i], s[i + 1], s[i + 2])] += 1
    c = cnt.most_common(1)[0][0]
    return tuple(v / 255 for v in c)


def parse_runs(text, base_bold, base_ital, base_color):
    """'**bold**' and '{#rrggbb|colored}' markup -> list of (text, (family-style index, color))."""
    runs = []; bold = base_bold; stack = []; buf = ""; i = 0
    def flush():
        nonlocal buf
        if buf: runs.append((buf, (1 if bold else 0) + (2 if base_ital else 0) if not (bold and base_ital) else 3, stack[-1] if stack else base_color)); buf = ""
    while i < len(text):
        if text.startswith("**", i): flush(); bold = not bold if True else bold; i += 2; continue
        m = re.match(r"\{#([0-9a-fA-F]{6})\|", text[i:])
        if m: flush(); stack.append(rgb(int(m.group(1), 16))); i += m.end(); continue
        if text[i] == "}" and stack: flush(); stack.pop(); i += 1; continue
        buf += text[i]; i += 1
    flush(); return runs


def layout(runs, fam, fobj, size, max_width):
    """Greedy word wrap. Returns lines; each line is a list of (word_text, (font, color), width, idx)."""
    words = []   # (text incl. trailing space, style) ; '\n' forces a break
    for text, idx, col in runs:
        for part in re.split(r"(\n)", text):
            if part == "\n": words.append(("\n", idx, col)); continue
            for w in re.findall(r"\S+\s*|\s+", part): words.append((w, idx, col))
    lines = [[]]; cur = 0
    for w, idx, col in words:
        if w == "\n": lines.append([]); cur = 0; continue
        f = fobj(fam, idx); wd = f.text_length(w, size)
        if max_width is not None and cur + f.text_length(w.rstrip(), size) > max_width and lines[-1]:
            lines.append([]); cur = 0
        lines[-1].append((w, (f, col), wd, idx)); cur += wd
    # trim trailing space width on each line (matters for right/center alignment)
    for ln in lines:
        if ln:
            t, fc, wd, idx = ln[-1]; stripped = t.rstrip()
            ln[-1] = (stripped, fc, fc[0].text_length(stripped, size), idx)
    return [ln for ln in lines if ln] or [[("", (fobj(fam, 0), (0, 0, 0)), 0, 0)]]


def apply(src, trans_json, out_pdf, blocks_json=None):
    doc = pymupdf.open(src)
    tmp = out_pdf + ".blocks.json"
    if blocks_json is None: extract(src, tmp); blocks_json = tmp
    blocks = json.load(open(blocks_json)); trans = json.load(open(trans_json))
    byid = {b["id"]: b for b in blocks}
    for k, v in list(trans.items()):
        if k not in byid and isinstance(v, dict) and "bbox" in v:   # a new block you define: bracket note over a stamp, signature, QR code...
            sz = v.get("size", 8); bb = v["bbox"]
            blocks.append({"id": k, "page": v.get("page", 0), "bbox": bb, "text": v["text"], "plain": v["text"], "baseline": v.get("baseline", bb[1] + sz), "pitch": sz * 1.2,
                           "nlines": 1, "font": v.get("font", "Helvetica"), "size": sz, "color": v.get("color", 0), "flags": 0, "align": v.get("align", "center")})
            byid[k] = blocks[-1]
    unknown = [k for k in trans if k not in byid]
    if unknown: sys.exit(f"unknown block ids in translations: {unknown}")
    warnings = []; placed = collections.defaultdict(list)
    # 1) paint out originals
    for pno, page in enumerate(doc):
        any_ = False
        for b in blocks:
            if b["page"] == pno and b["id"] in trans:
                r = pymupdf.Rect(b["bbox"]); b["_bg"] = bg_color(page, r)
                page.add_redact_annot(r + (-0.3, -0.3, 0.3, 0.3), fill=b["_bg"]); any_ = True
        if any_: page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    # 2) write English
    for pno, page in enumerate(doc):
        writers = {}; fonts = {}
        def fobj(fam, idx):
            if (fam, idx) not in fonts: fonts[(fam, idx)] = pymupdf.Font(fontfile=FONTS[fam][idx])
            return fonts[(fam, idx)]
        def writer(color):
            if color not in writers: writers[color] = pymupdf.TextWriter(page.rect, color=color)
            return writers[color]
        for b in blocks:
            if b["page"] != pno or b["id"] not in trans: continue
            t = trans[b["id"]]; t = {"text": t} if isinstance(t, str) else dict(t)
            align = t.get("align", b["align"]); size0 = t.get("size", b["size"]); fam = family_for(b["font"])
            base_bold = bool(b["flags"] & 16) or any(k in b["font"].lower() for k in ("bold", "black", "heavy"))
            base_ital = bool(b["flags"] & 2) or any(k in b["font"].lower() for k in ("italic", "oblique"))
            rect = pymupdf.Rect(b["bbox"]); basecol = rgb(b["color"])
            for k, d in (("extend_right", (0, 0, 1, 0)), ("extend_left", (-1, 0, 0, 0)), ("extend_down", (0, 0, 0, 1))):
                if k in t: rect = rect + tuple(v * t[k] for v in d)
            base_bold = t.get("bold", base_bold); base_ital = t.get("italic", base_ital)
            t["text"] = t["text"].replace("\\n", "\n")
            runs = parse_runs(t["text"], base_bold, base_ital, basecol)
            single = b["nlines"] == 1 and "\n" not in t["text"] and not t.get("wrap")
            size = size0
            below = [o["bbox"][1] for o in blocks if o["page"] == pno and o is not b and o["bbox"][1] >= b["bbox"][3] - 1
                     and min(o["bbox"][2], b["bbox"][2]) - max(o["bbox"][0], b["bbox"][0]) > 2]
            free_y = (min(below) if below else page.rect.height - 20) - 2
            grow = max(0.0, free_y - rect.y1) if not single else 0.0
            while True:
                lines = layout(runs, fam, fobj, size, None if single else rect.width)
                width = max(sum(w for _, _, w, _ in ln) for ln in lines)
                if single:
                    avail = rect.width if not t.get("overflow_ok", True) else 1e9
                    # a single line may grow past its original cell, toward free space, instead of shrinking
                    if align == "right": fits = rect.x1 - width >= 8
                    elif align == "center": fits = (rect.x0 + rect.x1) / 2 - width / 2 >= 8 and (rect.x0 + rect.x1) / 2 + width / 2 <= page.rect.width - 8
                    else: fits = rect.x0 + width <= page.rect.width - 8
                    if fits: break
                else:
                    if b["baseline"] + (len(lines) - 1) * b["pitch"] + size * 0.3 <= rect.y1 + 0.5 + grow + t.get("extend_down", 0): break
                if size <= size0 * 0.6: warnings.append(f"{b['id']}: does not fit even at 60% size: {t['text'][:60]!r}"); break
                size -= 0.25
            if size < size0 * 0.75: warnings.append(f"{b['id']}: shrunk to {size / size0:.0%}: {t['text'][:50]!r}")
            used = pymupdf.Rect(rect.x0, b["bbox"][1], rect.x1, b["bbox"][3])
            for li, ln in enumerate(lines):
                lw = sum(w for _, _, w, _ in ln); y = b["baseline"] + li * b["pitch"]
                x = rect.x0 if align in ("left", "justify") else rect.x1 - lw if align == "right" else (rect.x0 + rect.x1) / 2 - lw / 2
                if li == 0: used = pymupdf.Rect(x, b["bbox"][1], x + lw, b["bbox"][3])
                else: used |= pymupdf.Rect(x, y - size, x + lw, y + size * 0.3)
                for text_, (f, col), w, _ in ln:
                    writer(col).append((x, y), text_, font=f, fontsize=size); x += w
                if not single and li == 0: pass
            if "sub" in t:   # small italic second line, e.g. an approximate USD figure
                ss = t.get("sub_size", round(size * 0.8, 2)); f = fobj(fam, 2); sy = b["baseline"] + b["pitch"] * (len(lines) - 1) + ss * 1.25
                sw = f.text_length(t["sub"], ss); sx = rect.x0 if align == "left" else rect.x1 - sw if align == "right" else (rect.x0 + rect.x1) / 2 - sw / 2
                writer((0.35, 0.35, 0.35)).append((sx, sy), t["sub"], font=f, fontsize=ss); used |= pymupdf.Rect(sx, sy - ss, sx + sw, sy + ss * 0.3)
            placed[pno].append((b["id"], used))
        for w in writers.values(): w.write_text(page)
        # collision check between the areas we wrote and any other original text we kept
        kept = [pymupdf.Rect(b["bbox"]) for b in blocks if b["page"] == pno and b["id"] not in trans]
        for bid, used in placed[pno]:
            for k in kept:
                if _hit(used, k): warnings.append(f"{bid}: overlaps untouched text at {[round(v) for v in k]}")
        for (a, ra), (c, rc_) in [(x, y) for i, x in enumerate(placed[pno]) for y in placed[pno][i + 1:]]:
            if _hit(ra, rc_): warnings.append(f"{a} and {c} overlap")
    doc.save(out_pdf, garbage=3, deflate=True)
    if os.path.exists(tmp): os.remove(tmp)
    left = [b for b in blocks if b["id"] not in trans and re.search(r"[A-Za-zÀ-ÿ]{3,}", b["text"])]
    print(f"wrote {out_pdf}: {len(trans)} blocks replaced")
    if left:
        print("UNTOUCHED blocks that still contain words (translate them or confirm they are names/codes):")
        for b in left: print(f"  {b['id']}: {b['text'][:70]!r}")
    if warnings:
        print("WARNINGS:"); [print("  " + w) for w in warnings]


def ocr(src, out_pdf, lang="por"):  # lang: por | spa | fra | ita ... falls back to eng when the model is missing
    """Scanned/photographed pages: add an invisible text layer with tesseract so `extract` can find the blocks."""
    import subprocess, tempfile
    have = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True).stdout.split()
    if lang not in have:
        print(f"note: tesseract has no '{lang}' model here; using 'eng' for box positions only. Read the real text from the page image yourself.")
        lang = "eng"
    d = tempfile.mkdtemp(); doc = pymupdf.open(src); outs = []
    for i, p in enumerate(doc):
        png = f"{d}/p{i}.png"; p.get_pixmap(dpi=300).save(png)
        subprocess.run(["tesseract", png, f"{d}/p{i}", "-l", lang, "--psm", "4", "pdf"], check=True, capture_output=True); outs.append(f"{d}/p{i}.pdf")
    res = pymupdf.open()
    for o in outs: res.insert_pdf(pymupdf.open(o))
    res.save(out_pdf); print("searchable twin ->", out_pdf)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    if a[0] == "extract": extract(a[1], a[2])
    elif a[0] == "apply": apply(a[1], a[2], a[3], a[a.index("--blocks") + 1] if "--blocks" in a else None)
    elif a[0] == "ocr": ocr(a[1], a[2], a[a.index("--lang") + 1] if "--lang" in a else "por")
