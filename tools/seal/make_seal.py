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
