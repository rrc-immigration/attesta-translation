---
name: attesta-translation
description: Produce a certified English translation package for an Attesta Translation order (PT/ES/FR/IT to English, for USCIS), where the translated pages look exactly like the original and carry the Attesta certificate with the gold seal. Not for Rocha Ricomini cases.
---

# Attesta Translation: certified translation package

Use this for orders that belong to **Attesta Translation** (attestatranslation.com). For Rocha Ricomini Consulting or Migrei.ai cases, use `/certified-translation` instead. Attesta documents never carry Rocha Ricomini or Migrei.ai names, letterhead or seal, and the other way around.

The package has three parts, merged in this order: **translated document, Certificate of Translation Accuracy, original document.** Each source document gets its own translation, its own certificate (with its own page count) and itself. Never share one certificate between unrelated documents.

## The standard: a facsimile in English

The translated pages must look exactly like the original: **same page size and orientation, same fonts, same sizes, same colors, same bold and italic, same backgrounds, boxes, lines, logos and watermarks, same positions, same pagination.** A reviewer who lays the two side by side should see the same document, with only the language changed. Textual accuracy comes first, but looks are a requirement too, not a nicety.

The way to get there is to **keep the original page and replace only its text, in place** (Method A below). That keeps every logo, color, border and background pixel-for-pixel, instead of redrawing the page from scratch and approximating it. Rebuild a page from scratch (Method B) only when in-place replacement truly cannot work.

## Rules that never change

1. **Signature.** Never embed a signature image for anyone, on any certificate. The signature line is an empty underline. The translator signs the finished PDF in Adobe Acrobat (Fill & Sign, Sign Yourself). Tell the user they still need to sign before filing.
2. **Date.** The certificate date and "Date signed" are today's real date, computed when the file is generated. Never type a date by hand.
3. **Translator name.** Default is Sergio Rocha for Portuguese, Spanish and French. Italian has no assigned signer yet: if the language is Italian, stop and ask who signs. Never put a name on a certificate for someone who has not agreed to certify.
4. **No false claims.** USCIS does not approve or certify translators, so never write "USCIS approved" or "USCIS certified" on a certificate, a translation or a message. Certified here means the translator's signed statement of competence and accuracy (8 CFR 103.2(b)(3)). USCIS does not require notarization. This is not a sworn translation (tradução juramentada).
5. **Complete.** Translate every word, stamp text, seal text and margin note. Keep proper nouns, brand and product names, names of people and codes as they appear in the original (add a short bracketed gloss on first use only if it really helps, for example "Rende Fácil [savings product]"). Do not invent English names for institutions.
6. **Stamps, signatures, QR codes and barcodes** cannot be translated. Describe them in brackets in the same spot and footprint: `[Signature]`, `[Stamp: Name / Title]`, `[QR Code]`, `[Barcode]`. Do not reproduce them as pictures. **Official emblems, coats of arms and letterhead logos** stay as they are (they are institutional design, not an individual act).
7. **Currency.** If the source has Brazilian Reais, show an approximate USD figure with every BRL figure (the BRL figure stays primary and controlling), and pass `--brl-rate` to the certificate so it carries the exchange-rate note. Look up the day's rate before a real case and say which rate and date you used.
8. **Review.** The person who signs must review every page, including any AI-assisted draft. Say so in the hand-off.

## Workflow

### 0. Set up the working folder (once)

Create `mirror_pdf.py`, `attesta_cert.py` and `make_seal.py` from the code at the bottom of this file. Then run `python3 make_seal.py assets` once; it writes `assets/attesta_gold_seal.png`. Requirements: `pymupdf`, `pdfkit` with `wkhtmltopdf`, `fonttools`, `playwright` with Chromium, `Pillow`, `pypdf`, the Liberation and DejaVu fonts, and `tesseract` only for scans.

### 1. Inspect the source

Render every page to an image and look at it. Note the real page size (`pymupdf.open(f)[0].rect`), orientation, page count, whether the PDF has a text layer (`page.get_text()` returns words) or is a scan or phone photo, logos and stamps, background colors, and anything unreadable or cut off. Tell the user about unreadable parts before translating; never guess at them.

### 2. Translate: Method A, in place (default)

For a PDF with a text layer:

```bash
python3 mirror_pdf.py extract source.pdf blocks.json
```

`blocks.json` lists every text block with an id, position, font, size, color, alignment and its text. Table rows are split into one block per cell. Bold and colored words inside a block are marked as `**bold**` and `{#rrggbb|colored}`; keep those marks in your English so the mixed styling survives.

Write `translations.json`: a map from block id to the English text.

```json
{
  "p0b3": "Statement",
  "p0b6l1s0": {"text": "Credits: **R$ 0,00**", "sub": "(≈ $0.00)"},
  "p0b9g0": {"text": "Date", "align": "right"},
  "sig1":   {"page": 0, "bbox": [400, 700, 520, 740], "text": "[Signature]", "size": 8}
}
```

Rules for the file:
- Translate whole blocks, in natural English, not word by word. Use `\n` to force a line break (for example to keep two key-value lines apart).
- Leave out blocks that stay as they are: numbers, dates, names, codes. The tool then lists every untouched block that still has words, so you can confirm each one is a name or code and not a forgotten phrase.
- Dates: keep the original's date format unless the format would mislead an English reader (day/month order). If you change it, say so in the hand-off.
- Options per block: `align` (`left`, `right`, `center`), `bold` / `italic` (true or false, for when the source font is bold by weight and not by name), `size`, `extend_down` / `extend_right` / `extend_left` (points of extra room), `sub` (a small italic second line, used for the USD figure), `sub_size`.
- A block with `bbox` and a new id (like `sig1` above) paints out that region with its own background and writes your text there. Use it for the bracket notes over stamps, signatures and QR codes, and for text the extraction missed.
- Header cells above a right-aligned column should have `"align": "right"`.

Then build and look:

```bash
python3 mirror_pdf.py apply source.pdf translations.json translated.pdf --blocks blocks.json
```

Read what it prints. **UNTOUCHED** lists words you did not translate. **WARNINGS** lists text that had to shrink by more than 25%, text that collides with a neighbor, and text that did not fit. Fix each one: give the block `extend_down`, `extend_right` or `extend_left`, set `align`, or shorten the wording only if a shorter natural English phrase exists.

How it behaves: a single line may grow past its original cell toward free space instead of shrinking; a multi-line paragraph may grow downward into free space before it shrinks; sizes stay as in the original whenever there is room.

### 2b. Scans and phone photos

No text layer means no blocks. Run `python3 mirror_pdf.py ocr source.pdf twin.pdf --lang por` (use `spa`, `fra` or `ita` as needed). It adds an invisible text layer, so `extract` and `apply` work on `twin.pdf` with the same steps. If the language model is not installed, it falls back to English and prints a note: the box positions are still good, but you must read the real text from the page image yourself. On a scan, the font is unknown, so set `size`, `bold`, `italic` and `align` per block after looking at the page; the ink color is sampled from the image automatically. Anything in the image that is not text (stamps, signatures, handwriting) stays visible unless you cover it with a `bbox` block and a bracket note. Handwritten text gets translated in a bracketed note too, for example `[Handwritten: ...]`.

### 2c. Method B, rebuild (only when Method A cannot work)

Use it only when in-place replacement would collide or overflow in a way no `extend_*` fixes, for example when every BRL amount in a dense table needs a USD line that the row height cannot hold. Rebuild the page with reportlab using the exact values from `blocks.json` (page size, font family, size, color, positions) and the same lines, boxes and logos, and keep the page structure. Pagination may then grow; tell the user exactly what changed and why. Never silently drop text that does not fit: check that the longest line of every column is drawn in full.

### 3. Compare, page by page

Render the original and the translation of every page at the same scale, side by side, and look at each pair. Check: page size; fonts and sizes; colors; bold and italic; alignment of columns; logos, boxes, lines and backgrounds untouched; nothing overlapping, clipped or left in the source language except names and codes; every number, date and amount identical to the source; every BRL figure with its USD figure; stamp and signature areas replaced by bracket notes. Fix and rebuild until the pairs match.

### 4. Certificate

```bash
python3 attesta_cert.py --source "Certidao_Nascimento.pdf" --pages 1 \
  --language "Portuguese (Brazil)" --translator "Sergio Rocha" \
  [--order-no "AT-2026-0001"] [--brl-rate 5.16] [--pagesize A4] -o certificate.pdf
```

`--source` is the real file name, `--pages` is the number of source pages, `--pagesize A4` when the translated document is A4. The certificate has one image (the gold seal) and an empty signature line. `BUSINESS` at the top of `attesta_cert.py` holds the name, tagline, website, email and phone. Email and phone are `None` until the user decides them. Never use the user's account or personal email for Attesta.

### 5. Merge

```python
from pypdf import PdfReader, PdfWriter
w = PdfWriter()
for f in ("translated.pdf", "certificate.pdf", "original.pdf"):
    for p in PdfReader(f).pages:
        w.add_page(p)
w.write("final_package.pdf")
```

### 6. Final checks and hand-off

- Page counts add up (translated + 1 certificate + original).
- The certificate PDF has exactly one image and an empty signature line.
- Search the final PDF text for stray names: no "Rocha Ricomini" and no "Migrei" anywhere.
- Names, dates, page count and amounts on the certificate match the source.

Deliver the merged PDF with one line of context. In the same message tell the user briefly that (1) the signature line is blank and must be signed in Adobe before filing, (2) every page needs the signer's full review, (3) the exchange rate used, if any, and (4) anything that could not be matched exactly, such as a decorative font replaced by the closest standard one, or a date format changed.

## Fonts

The tool matches fonts by family: Arial, Helvetica and unknown sans-serif fonts map to Liberation Sans; Times and other serif fonts to Liberation Serif; Courier and monospaced fonts to Liberation Mono; Verdana, Tahoma and similar wide fonts to DejaVu Sans. These are metric-compatible, so line breaks and widths stay true. A decorative or script font cannot be matched exactly: mention it in the hand-off.

## Code

### mirror_pdf.py

```python
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
```

### attesta_cert.py

```python
"""
attesta_cert.py: Attesta Translation, Certificate of Translation Accuracy.

Same legal statements and signature policy as the Rocha Ricomini certificate
(8 CFR 103.2(b)(3): competence in both languages + accuracy), on Attesta's own
letterhead with the gold seal. Kept separate from the Rocha Ricomini template
on purpose.

SIGNATURE POLICY: the signature line is an empty underline. Never embed a
signature image. The translator signs the finished PDF in Adobe Acrobat
(Fill & Sign > Sign Yourself).

The certificate date and "Date signed" are always today's real date,
computed when the file is generated.

Usage:
    python3 attesta_cert.py --source "Certidao_Nascimento.pdf" --pages 1 \
        --language "Portuguese (Brazil)" --translator "Sergio Rocha" -o certificate.pdf
"""
import argparse, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))
SEAL = os.path.join(HERE, "assets", "attesta_gold_seal.png")

NAVY = "#14213D"
GOLD = "#B8902E"
INK = "#1B2236"

# Business details: change here once, every certificate picks it up.
BUSINESS = {
    "name": "ATTESTA TRANSLATION",
    "tagline": "Certified Translation Services",
    "website": "attestatranslation.com",
    "email": None,   # set when the real mailbox exists, e.g. "hello@attestatranslation.com"
    "phone": None,   # set when decided, e.g. "408 000 0000"
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def cert_html(source, pages, language, translator, order_no=None, brl_rate=None):
    today = datetime.date.today().strftime("%m/%d/%Y")
    seal = f'<img src="file://{SEAL}" style="width:118px;height:118px;">' if os.path.exists(SEAL) else ""
    contact_lines = "".join(f'<p class="sdet">{label}{esc(BUSINESS[k])}</p>' for k, label in (("email", "Email: "), ("phone", "Telephone: ")) if BUSINESS.get(k))
    order_row = f"<tr><th>Reference No.</th><td>{esc(order_no)}</td></tr>" if order_no else ""
    brl_note = ""
    if brl_rate:
        brl_note = (
            f'<p class="note">Note: All Brazilian Reais (BRL) figures appearing in the attached translation are '
            f'accompanied by an approximate U.S. Dollar (USD) equivalent, calculated at the exchange rate of '
            f'BRL {brl_rate:.2f} = USD 1.00 as quoted on {today}. The USD figures are provided solely for the '
            f'convenience of the reader and are approximate; the BRL figures stated in the original document '
            f'remain controlling.</p>'
        )
    return f"""<html><head><meta charset="utf-8"></head><body style="margin:0;">
<style>
  .page {{ width: 6.5in; margin: 0.75in auto 0 auto; }}
  .outer {{ border: 1.5px solid {NAVY}; padding: 5px; }}
  .inner {{ border: 1px solid {GOLD}; padding: 28px 40px 24px 40px; }}
  .serif {{ font-family: 'Times New Roman', Times, 'Liberation Serif', serif; }}
  .name {{ text-align:center; font-size: 21pt; font-weight: bold; letter-spacing: 3px; color: {NAVY}; margin: 0; }}
  .tag {{ text-align:center; font-size: 8.5pt; letter-spacing: 2.8px; color: {GOLD}; text-transform: uppercase; margin: 4px 0 14px 0; }}
  .rule {{ border: none; border-top: 1.5px solid {GOLD}; margin: 0 auto 18px auto; width: 60%; }}
  .title {{ text-align:center; font-size: 15pt; font-weight: bold; letter-spacing: 1.8px; color: {NAVY}; margin: 0 0 20px 0; text-transform: uppercase; }}
  .body p {{ font-size: 10.9pt; line-height: 1.55; color: {INK}; text-align: justify; margin: 0 0 13px 0; }}
  table.info {{ width:100%; border-collapse: collapse; margin: 16px 0 22px 0; }}
  table.info th {{ background: transparent; color: {NAVY}; font-size: 8.7pt; text-align:left; padding: 5px 10px 5px 8px; width: 32%;
      font-weight: bold; letter-spacing: .5px; text-transform: uppercase; border-bottom: 1px solid #bbb; border-left: 2.5px solid {GOLD}; }}
  table.info td {{ font-size: 10pt; padding: 5px 10px; border-bottom: 1px solid #ddd; color: #111; }}
  table.sign {{ width:100%; border-collapse: collapse; margin-top: 30px; }}
  table.sign td {{ vertical-align: bottom; padding: 0; }}
  .line {{ border-bottom: 1px solid {INK}; height: 34px; margin-bottom: 4px; }}
  .sname {{ font-size: 11.8pt; font-weight: bold; color: {NAVY}; margin: 0; }}
  .sdet {{ font-size: 9.2pt; color: #333; margin: 1px 0; }}
  .note {{ font-family: Arial, Helvetica, sans-serif; font-size: 7.8pt; color: #444; border-top: 1px solid #ccc; margin: 24px 0 0 0; padding-top: 9px; line-height: 1.4; }}
</style>
<div class="page serif"><div class="outer"><div class="inner">
  <p class="name">{BUSINESS['name']}</p>
  <p class="tag">{BUSINESS['tagline']}</p>
  <hr class="rule">
  <p class="title">Certificate of Translation Accuracy</p>
  <div class="body"><p>I, <b>{esc(translator)}</b>, hereby certify that I am fluent in both the {esc(language)} and English
  languages, and that I possess the requisite knowledge, training, and experience to competently translate documents
  between these two languages. I further certify that, to the best of my knowledge and ability, the attached translation
  is a true, complete, and accurate rendering of the original document identified below, and that this translation was
  prepared with professional care and diligence.</p></div>
  <table class="info">
    {order_row}
    <tr><th>Source Document</th><td>{esc(source)}</td></tr>
    <tr><th>Source Language</th><td>{esc(language)}</td></tr>
    <tr><th>Target Language</th><td>English (United States)</td></tr>
    <tr><th>Pages Translated</th><td>{esc(pages)}</td></tr>
    <tr><th>Certificate Date</th><td>{today}</td></tr>
  </table>
  <table class="sign"><tr>
    <td style="width:64%; padding-right:24px;">
      <div class="line"></div>
      <p class="sname">{esc(translator)}</p>
      <p class="sdet">Translator, Attesta Translation</p>
      <p class="sdet">{BUSINESS['website']}</p>{contact_lines}
      <p class="sdet">Date signed: <b>{today}</b></p>
    </td>
    <td style="width:36%; text-align:center;">{seal}</td>
  </tr></table>
  {brl_note}
</div></div></div>
</body></html>"""


def render(out_path, source, pages, language, translator, order_no=None, brl_rate=None, pagesize="Letter"):
    import pdfkit
    pdfkit.from_string(cert_html(source, pages, language, translator, order_no, brl_rate), out_path, options={
        "page-size": pagesize, "margin-top": "0in", "margin-bottom": "0.3in", "margin-left": "0in",
        "margin-right": "0in", "encoding": "UTF-8", "quiet": "", "enable-local-file-access": ""})
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True); ap.add_argument("--pages", required=True)
    ap.add_argument("--language", default="Portuguese (Brazil)"); ap.add_argument("--translator", default="Sergio Rocha")
    ap.add_argument("--order-no"); ap.add_argument("--brl-rate", type=float); ap.add_argument("--pagesize", default="Letter")
    ap.add_argument("-o", "--out", default="certificate.pdf")
    a = ap.parse_args()
    print(render(a.out, a.source, a.pages, a.language, a.translator, a.order_no, a.brl_rate, a.pagesize))
```

### make_seal.py

```python
import math, os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
f = TTFont(FONT); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f["hmtx"]; upm = f["head"].unitsPerEm

def glyph(ch):
    n = cmap[ord(ch)]; pen = SVGPathPen(gs); gs[n].draw(pen); return pen.getCommands(), hmtx[n][0]

def run_width(txt, size, track):
    s = size/upm
    return sum(glyph(c)[1]*s + track for c in txt) - track

def arc_text(txt, size, track, R, where, fill, dx=0, dy=0):
    """where: 'top' (glyphs outward from baseline radius R) or 'bottom' (glyphs inward)."""
    s = size/upm; total = run_width(txt, size, track)
    span = total / R  # radians
    out = []; pos = -span/2
    for c in txt:
        d, adv = glyph(c); w = adv*s
        phi = pos + (w/2)/R
        if where == "top":
            x = 120 + R*math.sin(phi); y = 120 - R*math.cos(phi); rot = math.degrees(phi)
        else:
            x = 120 + R*math.sin(phi); y = 120 + R*math.cos(phi); rot = -math.degrees(phi)
        if d:
            out.append(f'<path transform="translate({x+dx:.2f},{y+dy:.2f}) rotate({rot:.2f}) translate({-w/2:.2f},0) scale({s:.5f},{-s:.5f})" d="{d}" fill="{fill}"/>')
        pos += (w + track)/R
    return "\n".join(out)

def flat_text(txt, size, cx, base_y, fill, dx=0, dy=0):
    s = size/upm; w = run_width(txt, size, 0); x = cx - w/2; out = []
    for c in txt:
        d, adv = glyph(c)
        if d: out.append(f'<path transform="translate({x+dx:.2f},{base_y+dy:.2f}) scale({s:.5f},{-s:.5f})" d="{d}" fill="{fill}"/>')
        x += adv*s
    return "\n".join(out)

def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i*36); rr = r if i % 2 == 0 else r*0.42
        pts.append(f"{cx + rr*math.cos(a):.2f},{cy + rr*math.sin(a):.2f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'

def spikes(n, r_out, r_in):
    pts = []
    for i in range(2*n):
        a = math.radians(-90 + i*180.0/n); r = r_out if i % 2 == 0 else r_in
        pts.append(f"{120 + r*math.cos(a):.2f},{120 + r*math.sin(a):.2f}")
    return " ".join(pts)

N = 64
SP_OUT = spikes(N, 119, 114)
SP_IN = spikes(N, 117, 113)
DARK = "#6A4608"; LIGHT = "#FFF4BE"

def build(shadow=True, uid="g"):
    top = "ATTESTA TRANSLATION"; bot = "CERTIFIED"
    t_size, trk = 13.2, 1.9
    parts = []
    parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240" role="img" aria-label="Attesta Translation certified seal">
<defs>
<linearGradient id="{uid}foil" x1="0.12" y1="0.05" x2="0.88" y2="0.95">
<stop offset="0" stop-color="#FBE88A"/><stop offset="0.28" stop-color="#E2B94A"/><stop offset="0.5" stop-color="#C9962B"/><stop offset="0.72" stop-color="#E8C560"/><stop offset="1" stop-color="#A9761B"/></linearGradient>
<linearGradient id="{uid}rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF6CF"/><stop offset="0.5" stop-color="#F0D98A"/><stop offset="1" stop-color="#D9B55A"/></linearGradient>
<radialGradient id="{uid}center" cx="0.38" cy="0.32" r="0.8"><stop offset="0" stop-color="#FFF0A8" stop-opacity="0.9"/><stop offset="0.55" stop-color="#E5BD50" stop-opacity="0.2"/><stop offset="1" stop-color="#B68622" stop-opacity="0"/></radialGradient>
<linearGradient id="{uid}gloss" x1="0.1" y1="0" x2="0.7" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.5"/><stop offset="0.55" stop-color="#fff" stop-opacity="0.08"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="{uid}clip"><polygon points="{SP_OUT}"/></clipPath>
<filter id="{uid}sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#3A2A05" flood-opacity="0.38"/></filter>
</defs>''')
    parts.append(f'<g{f" filter=\"url(#{uid}sh)\"" if shadow else ""}>')
    parts.append(f'<polygon points="{SP_OUT}" fill="url(#{uid}rim)" stroke="#B88A24" stroke-width="0.6" stroke-linejoin="miter"/>')
    parts.append(f'<polygon points="{SP_IN}" fill="url(#{uid}foil)"/>')
    parts.append(f'<circle cx="120" cy="120" r="108" fill="url(#{uid}center)"/>')
    parts.append('</g>')
    # fine foil rings
    parts.append(f'<circle cx="120" cy="120" r="103" fill="none" stroke="{DARK}" stroke-opacity="0.7" stroke-width="1"/>')
    parts.append(f'<circle cx="120" cy="120" r="101.4" fill="none" stroke="{LIGHT}" stroke-opacity="0.8" stroke-width="0.6"/>')
    parts.append(f'<circle cx="120" cy="120" r="97" fill="none" stroke="{DARK}" stroke-width="1.6"/>')
    parts.append(f'<circle cx="120" cy="120" r="94" fill="none" stroke="{LIGHT}" stroke-opacity="0.8" stroke-width="0.7"/>')
    parts.append(f'<circle cx="120" cy="120" r="63" fill="none" stroke="{DARK}" stroke-width="1.6"/>')
    parts.append(f'<circle cx="120" cy="120" r="60.5" fill="none" stroke="{LIGHT}" stroke-opacity="0.8" stroke-width="0.7"/>')
    # ring text (light offset first = emboss)
    parts.append(arc_text(top, t_size, trk, 74, "top", LIGHT, 0.6, 0.7))
    parts.append(arc_text(top, t_size, trk, 74, "top", DARK))
    parts.append(arc_text(bot, 14, 3.4, 83.5, "bottom", LIGHT, 0.6, 0.7))
    parts.append(arc_text(bot, 14, 3.4, 83.5, "bottom", DARK))
    # stars flanking CERTIFIED on the bottom arc
    bspan = run_width(bot, 14, 3.4) / 83.5
    for sgn in (-1, 1):
        a = sgn*(bspan/2 + math.radians(11)); R = 78
        x = 120 + R*math.sin(a); y = 120 + R*math.cos(a)
        parts.append(star(x+0.5, y+0.7, 4.2, LIGHT)); parts.append(star(x, y, 4.2, DARK))
    # center monogram
    parts.append(flat_text("A", 92, 120, 148, LIGHT, 0.9, 1.1))
    parts.append(flat_text("A", 92, 120, 148, DARK))
    parts.append(f'<line x1="92" y1="160" x2="148" y2="160" stroke="{DARK}" stroke-width="1.4"/>')
    parts.append(f'<line x1="92" y1="161.6" x2="148" y2="161.6" stroke="{LIGHT}" stroke-opacity="0.8" stroke-width="0.6"/>')
    # gloss: sticker sheen across the upper-left, clipped to the disc
    parts.append(f'<g clip-path="url(#{uid}clip)"><path d="M12 120 C 12 60, 60 14, 128 12 C 150 12, 168 16, 184 24 C 120 40, 70 90, 52 168 C 30 156, 12 140, 12 120 Z" fill="url(#{uid}gloss)"/></g>')
    parts.append(f'<path d="M 36 78 A 92 92 0 0 1 96 30" fill="none" stroke="#fff" stroke-opacity="0.35" stroke-width="2" stroke-linecap="round"/>')
    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    # usage: python3 make_seal.py <output_dir>   -> writes attesta_gold_seal.png (600x600, transparent)
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    svg = build(False, "g").replace('width="240" height="240"', 'width="600" height="600"')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 600, "height": 600})
        pg.set_content('<html><body style="margin:0;background:transparent">' + svg + '</body></html>')
        pg.screenshot(path=os.path.join(out, "attesta_gold_seal.png"), omit_background=True,
                      clip={"x": 0, "y": 0, "width": 600, "height": 600})
        b.close()
    print("wrote", os.path.join(out, "attesta_gold_seal.png"))
```
