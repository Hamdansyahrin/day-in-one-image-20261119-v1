#!/usr/bin/env python3
"""Render entry.png for the make.fun news-image-20261119 entry.

One Day, One Page: the world news of Thursday 19 November 2026 drawn as a
single broadsheet front page, 1024 x 1024, with the Python standard library
plus Pillow. The page carries 45 stories: 3 illustrated leads, 10 illustrated
cards, a markets strip, a pinned world map and a 32-item index of briefs.

Design notes (broadsheet vernacular, chosen for a newspaper brief):
  palette  cream paper, ink navy, accent red, teal for science, gold markets
  type     Liberation Serif for the masthead and lead headlines,
           Liberation Sans for cards, the strip and the index
  layout   masthead / stat strip / 3 leads / 10 cards in two rows /
           map + index band; story numbers are real: they key the map pins

The renderer is deterministic: no randomness, no clock, no network.
Run it twice and the bytes are identical.
"""

from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W = 1024 * SCALE
H = 1024 * SCALE

PAPER = (246, 239, 221)
PAPER_DARK = (238, 229, 203)
INK = (22, 32, 58)
NAVY = (20, 38, 76)
RED = (179, 49, 42)
TEAL = (31, 110, 106)
GOLD = (178, 134, 28)
GREY = (96, 96, 92)
CARD_BG = (252, 249, 240)
RULE = (60, 60, 66)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size * SCALE)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap against a pixel width (in scaled units)."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, max_w, leading, max_lines=None):
    x, y = xy
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


class Box:
    """A rectangle in unscaled page coordinates, with scaled accessors."""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def s(self, fx, fy):
        return ((self.x + fx * self.w) * SCALE, (self.y + fy * self.h) * SCALE)

    def rect(self, fx0, fy0, fx1, fy1):
        x0, y0 = self.s(fx0, fy0)
        x1, y1 = self.s(fx1, fy1)
        return [x0, y0, x1, y1]


# --------------------------------------------------------------------------
# Illustrations. Each scene draws inside a Box using relative coordinates,
# so the same scene works at lead size and at card size.
# --------------------------------------------------------------------------

def scene_summit(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(168, 196, 224))
    d.rectangle(b.rect(0, 0.55, 1, 1), fill=(214, 205, 182))
    # skyline
    for fx, fw, fh in [(0.03, 0.10, 0.30), (0.16, 0.08, 0.22), (0.80, 0.09, 0.34),
                       (0.90, 0.07, 0.26), (0.68, 0.07, 0.20)]:
        d.rectangle(b.rect(fx, 0.55 - fh, fx + fw, 0.55), fill=(120, 142, 172))
    # three flags on poles behind the table
    for fx, cols in [(0.30, [(178, 34, 52)] * 3), (0.50, [(222, 41, 16)] * 3),
                     (0.70, [(255, 255, 255)] * 3)]:
        x0, y0 = b.s(fx, 0.16)
        x1, y1 = b.s(fx, 0.62)
        d.line([x0, y0, x0, y1], fill=INK, width=2 * SCALE)
    d.rectangle(b.rect(0.30, 0.16, 0.44, 0.34), fill=(255, 255, 255))  # US flag field
    d.rectangle(b.rect(0.30, 0.16, 0.44, 0.205), fill=(178, 34, 52))
    d.rectangle(b.rect(0.30, 0.25, 0.44, 0.295), fill=(178, 34, 52))
    d.rectangle(b.rect(0.30, 0.16, 0.375, 0.25), fill=(58, 84, 152))   # canton, top-left
    d.rectangle(b.rect(0.50, 0.16, 0.64, 0.34), fill=(222, 41, 16))    # China red
    for sx, sy in [(0.525, 0.20), (0.575, 0.185), (0.585, 0.225), (0.575, 0.265), (0.555, 0.29)]:
        cx, cy = b.s(sx, sy)
        r = 3 * SCALE if (sx, sy) == (0.525, 0.20) else 2 * SCALE
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 222, 0))
    d.rectangle(b.rect(0.70, 0.16, 0.84, 0.22), fill=(255, 255, 255))  # Russia tricolour
    d.rectangle(b.rect(0.70, 0.22, 0.84, 0.28), fill=(0, 57, 166))
    d.rectangle(b.rect(0.70, 0.28, 0.84, 0.34), fill=(213, 0, 50))
    # table and three seated figures
    d.rectangle(b.rect(0.14, 0.66, 0.86, 0.74), fill=(96, 62, 38))
    d.rectangle(b.rect(0.14, 0.74, 0.86, 0.97), fill=(122, 84, 50))
    for fx in (0.28, 0.50, 0.72):
        cx, cy = b.s(fx, 0.56)
        r = 0.055 * b.w * SCALE
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 190, 150))
        d.rectangle(b.rect(fx - 0.075, 0.615, fx + 0.075, 0.70), fill=NAVY)


def scene_bridge(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(226, 168, 120))              # dusk sky
    d.rectangle(b.rect(0, 0.58, 1, 1), fill=(52, 92, 128))             # sea
    for fy in (0.66, 0.78, 0.90):
        d.line([*b.s(0.04, fy), *b.s(0.96, fy)], fill=(90, 130, 165), width=SCALE)
    # deck, towers, cables
    d.rectangle(b.rect(0.02, 0.50, 0.98, 0.545), fill=(70, 70, 78))
    for fx in (0.30, 0.68):
        d.rectangle(b.rect(fx - 0.015, 0.20, fx + 0.015, 0.52), fill=(70, 70, 78))
        d.line([*b.s(fx, 0.20), *b.s(0.04, 0.50)], fill=(70, 70, 78), width=2 * SCALE)
        d.line([*b.s(fx, 0.20), *b.s(0.96, 0.50)], fill=(70, 70, 78), width=2 * SCALE)
    # the break: jagged gap, fire and smoke at mid-span
    d.rectangle(b.rect(0.455, 0.485, 0.545, 0.56), fill=(226, 168, 120))
    d.polygon([b.s(0.47, 0.545), b.s(0.50, 0.60), b.s(0.53, 0.545)], fill=(52, 92, 128))
    for fx, fy, r, col in [(0.50, 0.42, 0.075, (240, 120, 40)), (0.485, 0.36, 0.055, (250, 170, 60)),
                           (0.52, 0.33, 0.045, (240, 120, 40))]:
        cx, cy = b.s(fx, fy)
        rr = r * b.w * SCALE
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    for fx, fy, r in [(0.52, 0.24, 0.08), (0.59, 0.17, 0.10), (0.67, 0.12, 0.115)]:
        cx, cy = b.s(fx, fy)
        rr = r * b.w * SCALE
        d.ellipse([cx - rr, cy - rr * 0.6, cx + rr, cy + rr * 0.6], fill=(105, 100, 100))


def scene_gulf(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(240, 196, 130))
    d.rectangle(b.rect(0, 0.62, 1, 1), fill=(64, 110, 140))            # the Gulf
    d.rectangle(b.rect(0, 0.52, 0.62, 0.64), fill=(222, 190, 130))     # shore
    # radar dome base
    cx, cy = b.s(0.24, 0.52)
    r = 0.11 * b.w * SCALE
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(240, 240, 235))
    d.rectangle(b.rect(0.13, 0.52, 0.35, 0.60), fill=(150, 140, 120))
    # island target with flashes
    d.ellipse(b.rect(0.66, 0.66, 0.97, 0.82), fill=(200, 175, 120))
    for fx, fy in [(0.76, 0.70), (0.86, 0.74)]:
        cx, cy = b.s(fx, fy)
        rr = 0.05 * b.w * SCALE
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(245, 140, 50))
    # missile arcs from shore to island, drone silhouettes
    d.arc(b.rect(0.20, 0.05, 0.85, 0.75), 200, 320, fill=RED, width=3 * SCALE)
    d.arc(b.rect(0.28, 0.12, 0.90, 0.78), 205, 315, fill=INK, width=2 * SCALE)
    for fx, fy in [(0.55, 0.16), (0.68, 0.24)]:
        cx, cy = b.s(fx, fy)
        s = 0.035 * b.w * SCALE
        d.polygon([(cx - s, cy), (cx + s, cy), (cx, cy - s * 0.5)], fill=INK)
        d.line([cx - s * 1.5, cy + s * 0.4, cx + s * 1.5, cy + s * 0.4], fill=INK, width=2 * SCALE)


def scene_ipo(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(233, 238, 246))
    # rising chart
    pts = [b.s(fx, fy) for fx, fy in [(0.06, 0.82), (0.28, 0.70), (0.45, 0.74), (0.62, 0.52), (0.80, 0.34), (0.93, 0.20)]]
    d.line(pts, fill=TEAL, width=4 * SCALE)
    d.polygon([b.s(0.93, 0.20), b.s(0.84, 0.22), b.s(0.90, 0.30)], fill=TEAL)
    for fx in (0.25, 0.5, 0.75):
        d.line([*b.s(fx, 0.10), *b.s(fx, 0.88)], fill=(200, 208, 220), width=SCALE)
    # AI chip
    d.rectangle(b.rect(0.10, 0.12, 0.34, 0.36), fill=NAVY)
    d.rectangle(b.rect(0.17, 0.19, 0.27, 0.29), fill=GOLD)
    for f in (0.14, 0.22, 0.30):
        d.line([*b.s(f, 0.06), *b.s(f, 0.12)], fill=NAVY, width=2 * SCALE)
        d.line([*b.s(f, 0.36), *b.s(f, 0.42)], fill=NAVY, width=2 * SCALE)
    fnt = font(SANS_B, 30)
    cx, cy = b.s(0.66, 0.58)
    d.text((cx, cy), "$83", font=fnt, fill=INK, anchor="mm")


def scene_court(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(228, 224, 210))
    d.rectangle(b.rect(0.08, 0.18, 0.92, 0.24), fill=NAVY)            # pediment band
    d.polygon([b.s(0.04, 0.18), b.s(0.50, 0.05), b.s(0.96, 0.18)], fill=NAVY)
    for fx in (0.16, 0.34, 0.52, 0.70, 0.86):
        d.rectangle(b.rect(fx - 0.035, 0.24, fx + 0.035, 0.78), fill=(250, 248, 240))
    d.rectangle(b.rect(0.08, 0.78, 0.92, 0.86), fill=NAVY)
    # scales of justice in front
    cx, cy = b.s(0.50, 0.34)
    d.line([cx, cy, cx, cy + 0.34 * b.h * SCALE], fill=RED, width=3 * SCALE)
    d.line([*b.s(0.30, 0.40), *b.s(0.70, 0.40)], fill=RED, width=3 * SCALE)
    for fx in (0.30, 0.70):
        px, py = b.s(fx, 0.40)
        d.line([px, py, px - 0.07 * b.w * SCALE, py + 0.16 * b.h * SCALE], fill=RED, width=2 * SCALE)
        d.line([px, py, px + 0.07 * b.w * SCALE, py + 0.16 * b.h * SCALE], fill=RED, width=2 * SCALE)
        d.arc([px - 0.08 * b.w * SCALE, py + 0.10 * b.h * SCALE, px + 0.08 * b.w * SCALE,
               py + 0.24 * b.h * SCALE], 0, 180, fill=RED, width=3 * SCALE)


def scene_gta(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(250, 170, 90))
    d.rectangle(b.rect(0, 0.42, 1, 0.66), fill=(240, 110, 110))
    d.rectangle(b.rect(0, 0.66, 1, 1), fill=(44, 48, 84))
    cx, cy = b.s(0.50, 0.52)
    r = 0.16 * b.w * SCALE
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 120))
    # palms
    for fx, flip in [(0.10, 1), (0.90, -1)]:
        x0, y0 = b.s(fx, 0.98)
        x1, y1 = b.s(fx + 0.05 * flip, 0.52)
        d.line([x0, y0, x1, y1], fill=(30, 90, 60), width=4 * SCALE)
        for ang in (-0.5, -0.15, 0.2, 0.55):
            ex = x1 + flip * 0.10 * b.w * SCALE * (1 if ang > 0 else -1)
            ey = y1 + (ang * 0.10) * b.h * SCALE
            d.line([x1, y1, ex, ey], fill=(30, 110, 70), width=3 * SCALE)
    # sports car silhouette
    d.polygon([b.s(0.28, 0.86), b.s(0.38, 0.76), b.s(0.58, 0.74), b.s(0.70, 0.82),
               b.s(0.74, 0.86)], fill=(16, 16, 22))
    d.rectangle(b.rect(0.24, 0.86, 0.78, 0.90), fill=(16, 16, 22))
    for fx in (0.34, 0.66):
        cx, cy = b.s(fx, 0.905)
        rr = 0.035 * b.w * SCALE
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(200, 200, 210))
    fnt = font(SERIF, 34)
    d.text(b.s(0.065, 0.06), "VI", font=fnt, fill=(255, 244, 214))


def scene_voyager(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(10, 14, 34))
    stars = [(0.08, 0.15), (0.22, 0.32), (0.36, 0.10), (0.58, 0.22), (0.74, 0.12),
             (0.88, 0.30), (0.15, 0.55), (0.90, 0.58), (0.66, 0.44), (0.30, 0.70)]
    for fx, fy in stars:
        cx, cy = b.s(fx, fy)
        r = 2 * SCALE
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(235, 238, 255))
    # probe: big dish, boom, gold record
    cx, cy = b.s(0.42, 0.48)
    r = 0.20 * b.w * SCALE
    d.ellipse([cx - r, cy - r * 0.82, cx + r, cy + r * 0.82], outline=(230, 230, 235), width=3 * SCALE)
    d.ellipse([cx - r * 0.3, cy - r * 0.25, cx + r * 0.3, cy + r * 0.25], fill=(200, 200, 210))
    d.line([cx, cy, *b.s(0.72, 0.30)], fill=(200, 200, 210), width=3 * SCALE)
    gx, gy = b.s(0.74, 0.30)
    gr = 0.07 * b.w * SCALE
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=GOLD)
    d.line([cx, cy, *b.s(0.60, 0.78)], fill=(200, 200, 210), width=2 * SCALE)
    # tiny Earth and the day-long signal path
    ex, ey = b.s(0.90, 0.86)
    er = 0.045 * b.w * SCALE
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(90, 150, 230))
    for t in (0.25, 0.45, 0.65, 0.82):
        px = cx + (ex - cx) * t
        py = cy + (ey - cy) * t
        d.ellipse([px - 2 * SCALE, py - 2 * SCALE, px + 2 * SCALE, py + 2 * SCALE], fill=(255, 230, 130))


def scene_cyclone(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(120, 160, 190))
    d.rectangle(b.rect(0, 0.60, 1, 1), fill=(52, 100, 140))
    d.polygon([b.s(0, 0.60), b.s(0.35, 0.52), b.s(0.62, 0.60), b.s(0.62, 1), b.s(0, 1)],
              fill=(96, 140, 90))
    # spiral storm
    cx, cy = b.s(0.70, 0.34)
    for rr, a0 in [(0.30, 20), (0.23, 80), (0.16, 140), (0.09, 200)]:
        rw = rr * b.w * SCALE
        rh = rr * b.h * SCALE * 0.8
        d.arc([cx - rw, cy - rh, cx + rw, cy + rh], a0, a0 + 250, fill=(245, 245, 245), width=5 * SCALE)
    er = 0.035 * b.w * SCALE
    d.ellipse([cx - er, cy - er, cx + er, cy + er], fill=(70, 90, 120))
    # rain and a bent palm on the coast
    for fx in (0.08, 0.20, 0.32, 0.46):
        d.line([*b.s(fx, 0.66), *b.s(fx - 0.04, 0.80)], fill=(220, 235, 245), width=2 * SCALE)
    x0, y0 = b.s(0.16, 0.97)
    x1, y1 = b.s(0.26, 0.66)
    d.line([x0, y0, x1, y1], fill=(40, 90, 55), width=4 * SCALE)
    for s in (-1, 0.4, 1):
        d.line([x1, y1, x1 + s * 0.09 * b.w * SCALE, y1 + 0.05 * b.h * SCALE],
               fill=(40, 110, 65), width=3 * SCALE)


def scene_loan(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(24, 52, 116))
    # circle of EU stars (radius from the box height, so the ring never
    # spills out of a short card illustration)
    import math
    cx, cy = b.s(0.27, 0.50)
    R = 0.30 * b.h * SCALE
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + R * math.cos(a), cy + R * math.sin(a)
        r = 4 * SCALE
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 214, 0))
    # Ukraine ribbon, with the loan figure set inside its yellow band
    d.rectangle(b.rect(0.52, 0.22, 0.96, 0.44), fill=(0, 91, 187))
    d.rectangle(b.rect(0.52, 0.44, 0.96, 0.66), fill=(255, 213, 0))
    fnt = font(SANS_B, 17)
    d.text(b.s(0.74, 0.55), "€45bn", font=fnt, fill=NAVY, anchor="mm")


def scene_cop(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(250, 205, 130))
    cx, cy = b.s(0.76, 0.24)
    r = 0.13 * b.w * SCALE
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 130, 40))
    # cracked dry earth
    d.rectangle(b.rect(0, 0.62, 1, 1), fill=(176, 124, 72))
    for pts in [[(0.05, 0.70), (0.20, 0.78), (0.16, 0.90)], [(0.42, 0.66), (0.50, 0.80), (0.44, 0.94)],
                [(0.68, 0.72), (0.80, 0.80), (0.76, 0.92)]]:
        d.line([b.s(x, y) for x, y in pts], fill=(110, 74, 40), width=3 * SCALE)
    # thermometer globe
    gx, gy = b.s(0.26, 0.34)
    gr = 0.17 * b.w * SCALE
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(90, 150, 200))
    d.rectangle(b.rect(0.235, 0.10, 0.285, 0.30), fill=RED)
    d.ellipse(b.rect(0.215, 0.02, 0.305, 0.11), fill=RED)


def scene_ebola(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(210, 232, 214))
    # vaccine vial and syringe
    d.rectangle(b.rect(0.16, 0.30, 0.40, 0.88), fill=(240, 246, 250))
    d.rectangle(b.rect(0.16, 0.30, 0.40, 0.52), fill=TEAL)
    d.rectangle(b.rect(0.22, 0.18, 0.34, 0.30), fill=(120, 120, 125))
    d.rectangle(b.rect(0.20, 0.60, 0.36, 0.68), fill=(255, 255, 255))
    d.line([*b.s(0.60, 0.20), *b.s(0.82, 0.42)], fill=INK, width=4 * SCALE)
    d.rectangle(b.rect(0.56, 0.14, 0.68, 0.26), fill=(180, 190, 200))
    d.line([*b.s(0.82, 0.42), *b.s(0.90, 0.50)], fill=INK, width=2 * SCALE)
    # cross badge
    cx, cy = b.s(0.72, 0.72)
    s = 0.07 * b.w * SCALE
    d.rectangle([cx - s * 0.35, cy - s, cx + s * 0.35, cy + s], fill=RED)
    d.rectangle([cx - s, cy - s * 0.35, cx + s, cy + s * 0.35], fill=RED)


def scene_rain(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(105, 125, 150))
    for fx, fy, fw in [(0.08, 0.10, 0.42), (0.44, 0.06, 0.48), (0.24, 0.22, 0.40)]:
        d.ellipse(b.rect(fx, fy, fx + fw, fy + 0.20), fill=(225, 230, 236))
    for fx in (0.12, 0.26, 0.40, 0.54, 0.68, 0.82):
        for fy in (0.38, 0.55):
            d.line([*b.s(fx, fy), *b.s(fx - 0.03, fy + 0.13)], fill=(190, 215, 240), width=2 * SCALE)
    d.rectangle(b.rect(0, 0.82, 1, 1), fill=(60, 84, 108))
    for fx in (0.15, 0.45, 0.75):
        d.line([*b.s(fx, 0.88), *b.s(fx + 0.14, 0.88)], fill=(170, 200, 225), width=2 * SCALE)
    # umbrella
    cx, cy = b.s(0.50, 0.66)
    d.pieslice([cx - 0.20 * b.w * SCALE, cy - 0.20 * b.h * SCALE,
                cx + 0.20 * b.w * SCALE, cy + 0.20 * b.h * SCALE], 180, 360, fill=RED)
    d.line([cx, cy, cx, cy + 0.14 * b.h * SCALE], fill=INK, width=3 * SCALE)


def scene_gaza(d, b):
    d.rectangle(b.rect(0, 0, 1, 1), fill=(232, 205, 165))
    # city silhouette, some blocks broken
    blocks = [(0.04, 0.34, 0.14), (0.17, 0.26, 0.11), (0.29, 0.38, 0.12), (0.43, 0.30, 0.10),
              (0.55, 0.40, 0.12), (0.69, 0.28, 0.11), (0.82, 0.36, 0.13)]
    for fx, fh, fw in blocks:
        d.rectangle(b.rect(fx, 0.78 - fh, fx + fw, 0.78), fill=(150, 138, 122))
    d.polygon([b.s(0.29, 0.40), b.s(0.35, 0.52), b.s(0.41, 0.40)], fill=(232, 205, 165))
    d.rectangle(b.rect(0, 0.78, 1, 1), fill=(190, 170, 140))
    # the Yellow Line
    d.line([*b.s(0.50, 0.06), *b.s(0.50, 0.97)], fill=(250, 200, 0), width=5 * SCALE)
    # aid truck on the near side
    d.rectangle(b.rect(0.06, 0.82, 0.26, 0.92), fill=(245, 245, 245))
    d.rectangle(b.rect(0.26, 0.86, 0.34, 0.92), fill=TEAL)
    for fx in (0.11, 0.29):
        cx, cy = b.s(fx, 0.935)
        rr = 0.028 * b.w * SCALE
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=INK)
    cx, cy = b.s(0.16, 0.87)
    s = 0.035 * b.w * SCALE
    d.rectangle([cx - s * 0.3, cy - s, cx + s * 0.3, cy + s], fill=RED)
    d.rectangle([cx - s, cy - s * 0.3, cx + s, cy + s * 0.3], fill=RED)


SCENES = [scene_summit, scene_bridge, scene_gulf, scene_ipo, scene_court,
          scene_gta, scene_voyager, scene_cyclone, scene_loan, scene_cop,
          scene_ebola, scene_rain, scene_gaza]

LEADS = [
    ("SHENZHEN, CHINA", "Three presidents, one table in Shenzhen",
     "Trump, Xi and Putin hold their first three-way summit on the APEC "
     "sidelines. Ukraine, Iran, nuclear arms, trade and AI fill the agenda."),
    ("CRIMEA", "Crimean Bridge hit for the third time this week",
     "Ukraine strikes the Kerch Strait crossing again, closing traffic "
     "while damage is assessed. Kyiv's bridge campaign is intensifying."),
    ("THE GULF", "Iran hits Gulf states after US strike on Qeshm",
     "Tehran answers the US attack on Qeshm island with strikes across "
     "the Gulf. A tanker is hit near Hormuz; crews are reported safe."),
]

CARDS = [
    ("NEW YORK", "Anthropic's record IPO: $83 a share",
     "The AI giant prices the biggest listing on record, yet AI jitters still drag world markets down."),
    ("MYANMAR / THE HAGUE", "World court to rule on Myanmar genocide case",
     "The UN's top court prepares its judgment on the Rohingya genocide claims against Myanmar."),
    ("VICE CITY", "GTA VI goes on sale after a 13-year wait",
     "Gamers flood into Vice City as the most anticipated game ever begins its global rollout."),
    ("DEEP SPACE", "Voyager 1 reaches one light-day from Earth",
     "NASA's farthest probe crosses a new frontier: its signal now takes a full day to reach home."),
    ("BAY OF BENGAL", "Cyclone Akvan bears down on India's east coast",
     "Odisha shuts schools across seven districts as the storm nears the Andhra-Odisha shore."),
    ("BERLIN / BRUSSELS", "EU proposes a €45bn loan for Ukraine",
     "Brussels' plan would be repaid once Russia pays reparations, as allies meet in Berlin."),
    ("ANTALYA, TÜRKIYE", "COP31 deadlock as climate check launches",
     "Talks stall in Antalya; India demands equity and that climate finance promises be honoured."),
    ("DR CONGO", "Ebola vaccines head for trials in DR Congo",
     "Strain-specific Ebola vaccines will be trialled in the east of the country."),
    ("CALIFORNIA", "Record rain: atmospheric river soaks California",
     "San Francisco is drenched as a record atmospheric river slams into the US West Coast."),
    ("GAZA", "Israel pushes beyond the Yellow Line in Gaza",
     "A ground operation advances in central Gaza as four allies demand aid reach the flooded enclave."),
]

BRIEFS = [
    "Democrats win Alaska: 56-seat Senate majority",
    "Jeffries tipped as first Black US House Speaker",
    "Israel delays E1 settlement plan in West Bank",
    "Trump: Iran exploring chemical, bio weapons",
    "Ethiopia, Eritrea mass troops on their border",
    "1 in 4 children live in conflict zones: UN",
    "Five EU states plan Rwanda asylum transfers",
    "Sudan: drones drive the civilian toll in El Dabba",
    "IAEA: North Korea expanded uranium enrichment",
    "Turkish court sentences Imamoglu in CHP case",
    "Pew: Islam to pass Christianity by 2035",
    "Suneung: Korea pauses flights for exam day",
    "EU governments approve Indonesia trade deal",
    "Australia's jobless rate rises to 4.9%",
    "IMF deal unlocks $2.3bn for Egypt",
    "US loses its measles elimination status",
    "Alzheimer's, brain-tumour advances in UK studies",
    "Fiji, Tonga declare El Niño drought emergencies",
    "Waymo pulls its robotaxis from US freeways",
    "Antarctic blue whales up 10x since whaling ended",
    "Webb telescope confirms a rare stellar merger",
    "NASA readies CRS-25 cargo launch coverage",
    "US, Venezuela restore military cooperation",
    "Isolated Awá group makes rare contact in Brazil",
    "Milei bill to suspend primaries advances",
    "Bangladesh unrest over Hasina return reports",
    "Saudi all-clear after alerts in three cities",
    "France: 4th weekend of cost-of-living protests",
    "Herzog asks Eisenkot to form Israel's government",
    "Bancroft: whole team knew of ball-tampering",
    "Alcaraz beats Medvedev at the ATP Finals",
    "Cambridge Dictionary: 'human', word of the year",
]

STATS = [("S&P 500", "7,324", "-0.23%"), ("FTSE 100", "10,551", "-1.30%"),
         ("HANG SENG", "—", "-2.78%"), ("BRENT", "$89.3", "+0.15%"),
         ("US 10-YR", "5.07%", "-0.73%"), ("WORLD MOOD", "UNEASY", "")]

# Coarse continent outlines as (lon, lat) polygons for the pinned map.
NORTH_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
                 (-80, 62), (-76, 58), (-70, 55), (-65, 50), (-70, 44), (-74, 40),
                 (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 29), (-97, 26),
                 (-102, 20), (-108, 21), (-112, 27), (-117, 33), (-122, 37),
                 (-124, 46), (-132, 55), (-152, 60), (-165, 60)]
SOUTH_AMERICA = [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
                 (-38, -5), (-40, -20), (-48, -27), (-55, -33), (-62, -39),
                 (-65, -45), (-68, -52), (-72, -54), (-74, -48), (-73, -40),
                 (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-81, -4),
                 (-80, 1), (-77, 5)]
AFRICA = [(-17, 15), (-10, 29), (-6, 35), (10, 37), (20, 32), (30, 31), (35, 28),
          (43, 12), (49, 11), (51, 9), (44, -1), (40, -10), (38, -20), (35, -27),
          (31, -31), (20, -35), (17, -32), (15, -27), (12, -18), (13, -11),
          (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 12)]
EURASIA = [(-9, 37), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (18, 56),
           (24, 59), (30, 60), (28, 66), (40, 67), (55, 68), (75, 72), (95, 76),
           (110, 74), (130, 72), (155, 70), (178, 66), (178, 62), (162, 58),
           (156, 51), (142, 52), (140, 45), (135, 44), (132, 43), (127, 40),
           (129, 36), (126, 34), (122, 31), (120, 27), (114, 22), (108, 18),
           (106, 9), (103, 1), (100, 7), (98, 10), (94, 17), (91, 22), (88, 22),
           (86, 20), (80, 15), (77, 8), (73, 18), (68, 23), (61, 25), (57, 27),
           (51, 28), (48, 30), (54, 26), (58, 23), (59, 22), (52, 15), (45, 12),
           (43, 12), (40, 20), (35, 28), (34, 31), (36, 36), (30, 36), (27, 37),
           (23, 36), (19, 40), (16, 38), (15, 40), (12, 44), (8, 44), (3, 43), (-2, 37)]
AUSTRALIA = [(113, -22), (114, -29), (115, -34), (119, -35), (126, -32), (132, -32),
             (135, -35), (139, -37), (145, -38), (150, -37), (153, -31), (153, -26),
             (146, -19), (142, -11), (141, -14), (136, -15), (135, -12), (131, -11),
             (126, -14), (122, -17), (117, -20)]
ISLANDS = [[(44, -16), (47, -15), (50, -18), (49, -23), (46, -25), (44, -21)],
           [(-3, 50), (-5, 53), (-3, 56), (-1, 58), (0, 53)],
           [(138, 35), (140, 36), (141, 40), (143, 43), (145, 44), (142, 45), (139, 38)],
           [(95, -2), (102, -4), (110, -3), (118, -2), (125, -3), (131, -3),
            (125, 0), (115, 0), (104, 1), (96, 1)]]
LAND = [NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EURASIA, AUSTRALIA] + ISLANDS

# Map pins for the 13 illustrated stories: (story number, lon, lat)
PINS = [(1, 114, 22), (2, 34, 45), (3, 56, 27), (4, -74, 41), (5, 97, 20),
        (6, -80, 26), (8, 88, 14), (9, 13, 52), (10, 27, 37), (11, 23, -2),
        (12, -120, 37), (13, 37, 29)]


def draw_map(d, box):
    d.rectangle([box.x * SCALE, box.y * SCALE, (box.x + box.w) * SCALE,
                 (box.y + box.h) * SCALE], fill=(203, 220, 228))
    def proj(lon, lat):
        x = box.x + (lon + 180) / 360 * box.w
        y = box.y + (78 - lat) / 138 * box.h
        return (x * SCALE, y * SCALE)
    for poly in LAND:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(146, 172, 128))
    for num, lon, lat in PINS:
        cx, cy = proj(lon, lat)
        r = 9 * SCALE
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        fnt = font(SANS_B, 10 if num < 10 else 9)
        d.text((cx, cy - 1 * SCALE), str(num), font=fnt, fill=(255, 255, 255), anchor="mm")
    # pin 7: Voyager, off the top of the map with a dashed trail
    cx, cy = proj(-150, 62)
    ex, ey = box.x + box.w * 0.16, box.y + 8
    ex, ey = ex * SCALE, ey * SCALE
    for t in (0.3, 0.55, 0.8):
        px, py = cx + (ex - cx) * t, cy + (ey - cy) * t
        d.ellipse([px - 2 * SCALE, py - 2 * SCALE, px + 2 * SCALE, py + 2 * SCALE], fill=NAVY)
    r = 9 * SCALE
    d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=NAVY)
    d.text((ex, ey - 1 * SCALE), "7", font=font(SANS_B, 10), fill=(255, 255, 255), anchor="mm")


def pin_badge(d, x, y, num):
    r = 11 * SCALE
    cx, cy = x * SCALE, y * SCALE
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.text((cx, cy - 1 * SCALE), str(num), font=font(SANS_B, 12), fill=(255, 255, 255), anchor="mm")


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 18  # page margin, unscaled px

    # ---- masthead ------------------------------------------------------
    d.text(((M + 2) * SCALE, 12 * SCALE), "THE WORLD IN ONE IMAGE",
           font=font(SANS_B, 13), fill=RED)
    d.text(((1024 - M - 2) * SCALE, 12 * SCALE), "45 STORIES · ONE PAGE",
           font=font(SANS_B, 13), fill=INK, anchor="ra")
    d.text((512 * SCALE, 30 * SCALE), "Thursday, 19 November 2026",
           font=font(SERIF, 43), fill=NAVY, anchor="ma")
    d.line([M * SCALE, 86 * SCALE, (1024 - M) * SCALE, 86 * SCALE], fill=INK, width=3 * SCALE)
    d.line([M * SCALE, 91 * SCALE, (1024 - M) * SCALE, 91 * SCALE], fill=INK, width=SCALE)

    # ---- markets strip ---------------------------------------------------
    d.rectangle([M * SCALE, 97 * SCALE, (1024 - M) * SCALE, 127 * SCALE], fill=NAVY)
    sx = M + 12
    for name, value, delta in STATS:
        fnt_n, fnt_v = font(SANS_B, 12), font(SANS_B, 13)
        d.text((sx * SCALE, 105 * SCALE), name, font=fnt_n, fill=(170, 190, 225))
        w_n = d.textlength(name, font=fnt_n) / SCALE
        d.text(((sx + w_n + 6) * SCALE, 104 * SCALE), value, font=fnt_v, fill=(255, 255, 255))
        w_v = d.textlength(value, font=fnt_v) / SCALE
        if delta:
            col = (255, 150, 140) if delta.startswith("-") else (150, 235, 170)
            d.text(((sx + w_n + w_v + 11) * SCALE, 105 * SCALE), delta, font=fnt_n, fill=col)
            w_d = d.textlength(delta, font=fnt_n) / SCALE
        else:
            w_d = 0
        sx += w_n + w_v + w_d + 34

    # ---- leads -----------------------------------------------------------
    lead_y, lead_h, gap = 135, 262, 10
    lead_w = (1024 - 2 * M - 2 * gap) // 3
    for i, (kicker, head, sub) in enumerate(LEADS):
        x = M + i * (lead_w + gap)
        d.rectangle([x * SCALE, lead_y * SCALE, (x + lead_w) * SCALE,
                     (lead_y + lead_h) * SCALE], fill=CARD_BG, outline=RULE, width=SCALE)
        SCENES[i](d, Box(x + 5, lead_y + 5, lead_w - 10, 138))
        pin_badge(d, x + 17, lead_y + 17, i + 1)
        d.text(((x + 10) * SCALE, (lead_y + 149) * SCALE), kicker, font=font(SANS_B, 10), fill=RED)
        yy = text_block(d, ((x + 10) * SCALE, (lead_y + 163) * SCALE), head,
                        font(SERIF, 18), INK, (lead_w - 20) * SCALE, 22 * SCALE, max_lines=2)
        text_block(d, ((x + 10) * SCALE, yy + 3 * SCALE), sub,
                   font(SANS, 11.5), (52, 52, 56), (lead_w - 20) * SCALE, 15 * SCALE, max_lines=4)

    # ---- cards, two rows of five -----------------------------------------
    card_y0, card_h, cgap = 403, 156, 8
    card_w = (1024 - 2 * M - 4 * cgap) // 5
    for i, (kicker, head, sub) in enumerate(CARDS):
        row, col = divmod(i, 5)
        x = M + col * (card_w + cgap)
        y = card_y0 + row * (card_h + cgap)
        num = i + 4
        d.rectangle([x * SCALE, y * SCALE, (x + card_w) * SCALE, (y + card_h) * SCALE],
                    fill=CARD_BG, outline=RULE, width=SCALE)
        SCENES[num - 1](d, Box(x + 4, y + 4, card_w - 8, 62))
        pin_badge(d, x + 14, y + 14, num)
        d.text(((x + 8) * SCALE, (y + 70) * SCALE), kicker, font=font(SANS_B, 8.5), fill=RED)
        yy = text_block(d, ((x + 8) * SCALE, (y + 82) * SCALE), head,
                        font(SANS_B, 12), INK, (card_w - 16) * SCALE, 15 * SCALE, max_lines=2)
        text_block(d, ((x + 8) * SCALE, yy + 2 * SCALE), sub,
                   font(SANS, 9.5), (52, 52, 56), (card_w - 16) * SCALE, 12.5 * SCALE, max_lines=3)

    # ---- bottom band: map + index ----------------------------------------
    bot_y = card_y0 + 2 * card_h + cgap + 8
    d.line([M * SCALE, (bot_y - 4) * SCALE, (1024 - M) * SCALE, (bot_y - 4) * SCALE],
           fill=INK, width=2 * SCALE)
    d.text((M * SCALE, bot_y * SCALE), "WHERE IT HAPPENED — THE 13 ILLUSTRATED STORIES",
           font=font(SANS_B, 11), fill=NAVY)
    draw_map(d, Box(M, bot_y + 20, 452, 208))
    d.text((M * SCALE, (bot_y + 234) * SCALE),
           "Pin 7 is Voyager 1: one light-day out, off the map entirely.",
           font=font(SANS, 10), fill=GREY)

    ix = M + 452 + 16
    iw = 1024 - M - ix
    d.text((ix * SCALE, bot_y * SCALE), "ALSO ON THURSDAY — 32 MORE STORIES",
           font=font(SANS_B, 11), fill=NAVY)
    col_w = (iw - 12) // 2
    for j, brief in enumerate(BRIEFS):
        col, row = divmod(j, 16)
        x = ix + col * (col_w + 12)
        y = bot_y + 20 + row * 14.5
        d.text((x * SCALE, y * SCALE), "· " + brief, font=font(SANS, 10),
               fill=(40, 40, 46))
    d.line([M * SCALE, (bot_y + 253) * SCALE, (1024 - M) * SCALE, (bot_y + 253) * SCALE],
           fill=INK, width=SCALE)
    d.text((M * SCALE, (bot_y + 259) * SCALE),
           "One Day, One Page — a program-drawn front page, no photographs",
           font=font(SANS, 10), fill=GREY)
    d.text(((1024 - M) * SCALE, (bot_y + 259) * SCALE),
           "Sources: the wires of 19 Nov 2026",
           font=font(SANS, 10), fill=GREY, anchor="ra")

    img = img.resize((1024, 1024), Image.LANCZOS)
    img.save("entry.png", optimize=True)
    return img


if __name__ == "__main__":
    render()
    print("wrote entry.png")
