"""Sum up 26 November's world news in one image — make.fun entry.

Draws a 1024x1024 PNG infographic (pure Python standard library, no
network, fully deterministic) with six verified stories first reported on
Thursday 26 November 2026, and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png).
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# 5x7 pixel font: each glyph is 7 rows of 5 bits (MSB = leftmost pixel).
FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14), "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31), "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15), "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14), "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17), "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14), "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13), "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14), "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10), "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14), "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31), "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14), "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0), ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8), "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 14, 0, 0, 0), ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8), "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4), "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8), "&": (12, 18, 20, 8, 21, 18, 13),
    "%": (25, 26, 2, 4, 8, 11, 19), "$": (4, 15, 20, 14, 5, 30, 4),
    "/": (1, 2, 2, 4, 8, 8, 16), "+": (0, 4, 4, 14, 4, 4, 0),
    "=": (0, 0, 31, 0, 31, 0, 0), '"': (10, 10, 0, 0, 0, 0, 0),
    "•": (0, 0, 12, 12, 12, 0, 0),
}

# ------------------------------------------------------------- canvas -----
NAVY = (22, 38, 63)
GOLD = (201, 162, 39)
PAPER = (245, 241, 232)
INK = (26, 26, 26)
GREY = (85, 85, 85)
WHITE = (255, 255, 255)
BORDER = (216, 210, 196)

# (accent colour, kicker, headline, deck, icon, source)
STORIES = [
    ((168, 50, 50), "NORTH KOREA",
     "NORTH KOREA EXPELS SWISS ENVOY",
     "PYONGYANG ORDERS SWITZERLAND TO SHUT ITS NEW OFFICE WITHIN 48 HOURS",
     "flag", "AFP"),
    ((31, 92, 139), "SPACE",
     "PAKISTANI ASTRONAUT REACHES TIANGONG",
     "ZEESHAN ALI FLIES ON SHENZHOU-24, THE FIRST FOREIGNER ABOARD CHINA'S STATION",
     "rocket", "INDIAN EXPRESS"),
    ((14, 124, 107), "BANGLADESH",
     "GARMENT WORKERS WIN 36% PAY RISE",
     "BANGLADESH RAISES MINIMUM WAGE FOR GARMENT WORKERS BY MORE THAN A THIRD",
     "factory", "MANILA TIMES"),
    ((91, 75, 138), "PACIFIC",
     "AUSTRALIA SIGNS PACT WITH SOLOMON ISLANDS",
     "DEAL SEEN AS A CHECK ON CHINA'S INFLUENCE IN THE PACIFIC",
     "islands", "AFP"),
    ((201, 106, 27), "UKRAINE",
     "US SHELVES RUSSIA BUSINESS-DEAL PEACE PLAN",
     "FINANCIAL TIMES REPORTS THE TRADE-FOR-PEACE ROUTE IS OFF THE TABLE",
     "document", "FINANCIAL TIMES"),
    ((46, 125, 50), "CRICKET",
     "1,220 PLAYERS SIGN UP FOR IPL AUCTION",
     "RECORD REGISTRATIONS FOR THE 2027 INDIAN PREMIER LEAGUE SALE",
     "cricket", "INDIAN EXPRESS"),
]


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x0 + a - thick // 2, y0 + b - thick // 2, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def circle(self, cx, cy, r, c, thick=2):
        for a in range(360):
            t = math.radians(a)
            for k in range(thick):
                self.set(cx + int((r - k) * math.cos(t)),
                         cy + int((r - k) * math.sin(t)), c)

    def triangle(self, p1, p2, p3, c):
        pts = sorted((p1, p2, p3), key=lambda p: p[1])
        (x1, y1), (x2, y2), (x3, y3) = pts
        if y1 == y3:
            return
        def interp(y, pa, pb):
            if pa[1] == pb[1]:
                return pa[0]
            return pa[0] + (pb[0] - pa[0]) * (y - pa[1]) / (pb[1] - pa[1])
        for y in range(y1, y3 + 1):
            if y < y2:
                xa, xb = interp(y, pts[0], pts[1]), interp(y, pts[0], pts[2])
            else:
                xa, xb = interp(y, pts[1], pts[2]), interp(y, pts[0], pts[2])
            if xa > xb:
                xa, xb = xb, xa
            self.fill_rect(int(xa), y, int(xb) - int(xa) + 1, 1, c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, c):
    s = s.upper()
    for i, ch in enumerate(s):
        glyph = FONT.get(ch, FONT[" "])
        ox = x + i * 6 * scale
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.fill_rect(ox + col * scale, y + row * scale,
                                 scale, scale, c)


def wrap(text, max_w, scale):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- icons -----
def draw_icon(cv, cx, cy, kind, accent):
    cv.fill_circle(cx, cy, 30, accent)
    w = WHITE
    if kind == "flag":
        cv.line(cx - 12, cy - 18, cx - 12, cy + 18, w, 3)
        cv.triangle((cx - 11, cy - 18), (cx + 16, cy - 11), (cx - 11, cy - 4), w)
        cv.fill_rect(cx - 18, cy + 18, 36, 3, w)
    elif kind == "rocket":
        cv.triangle((cx, cy - 20), (cx - 8, cy - 2), (cx + 8, cy - 2), w)
        cv.fill_rect(cx - 8, cy - 2, 16, 16, w)
        cv.triangle((cx - 8, cy - 2), (cx - 15, cy + 12), (cx - 8, cy + 10), w)
        cv.triangle((cx + 8, cy - 2), (cx + 15, cy + 12), (cx + 8, cy + 10), w)
        cv.triangle((cx, cy + 20), (cx - 5, cy + 12), (cx + 5, cy + 12),
                    (255, 176, 32))
        cv.fill_rect(cx - 3, cy + 2, 6, 6, NAVY)
    elif kind == "factory":
        cv.fill_rect(cx - 16, cy - 2, 32, 20, w)
        cv.fill_rect(cx - 16, cy - 14, 6, 12, w)
        cv.fill_rect(cx - 5, cy - 18, 6, 16, w)
        cv.triangle((cx - 16, cy - 2), (cx - 8, cy - 10), (cx, cy - 2), NAVY)
        cv.triangle((cx, cy - 2), (cx + 8, cy - 10), (cx + 16, cy - 2), NAVY)
        cv.fill_rect(cx - 12, cy + 6, 6, 6, NAVY)
        cv.fill_rect(cx + 2, cy + 6, 6, 6, NAVY)
    elif kind == "islands":
        cv.fill_circle(cx - 11, cy - 2, 11, w)
        cv.fill_circle(cx + 12, cy - 8, 9, w)
        cv.fill_circle(cx + 2, cy + 12, 6, w)
        cv.line(cx - 18, cy + 18, cx - 8, cy + 18, w, 2)
        cv.line(cx + 6, cy + 18, cx + 18, cy + 18, w, 2)
    elif kind == "document":
        cv.fill_rect(cx - 12, cy - 16, 24, 32, w)
        cv.triangle((cx + 12, cy - 16), (cx + 12, cy - 6), (cx + 2, cy - 16),
                    NAVY)
        for i, yy in enumerate((-6, 0, 6)):
            cv.fill_rect(cx - 7, cy + yy, 14 if i < 2 else 9, 2, accent)
    elif kind == "cricket":
        cv.line(cx - 12, cy + 14, cx + 8, cy - 14, w, 5)
        cv.line(cx + 8, cy - 14, cx + 14, cy - 18, w, 3)
        cv.fill_circle(cx - 12, cy - 10, 7, (255, 176, 32))
        cv.line(cx - 16, cy - 13, cx - 8, cy - 7, NAVY, 1)


# -------------------------------------------------------------- render ----
def render():
    cv = Canvas(W, H, PAPER)

    # Header band.
    cv.fill_rect(0, 0, W, 152, NAVY)
    draw_text(cv, 40, 26, "WORLD NEWS", 7, WHITE)
    draw_text(cv, 40, 98, "THURSDAY 26 NOVEMBER 2026", 3, GOLD)
    # Globe emblem, top right.
    gx, gy, gr = 918, 74, 52
    cv.circle(gx, gy, gr, GOLD, 3)
    cv.circle(gx, gy, int(gr * 0.55), GOLD, 2)
    cv.line(gx - gr, gy, gx + gr, gy, GOLD, 2)
    cv.line(gx, gy - gr, gx, gy + gr, GOLD, 2)
    for k in (-1, 1):
        cv.line(gx + k * 26, gy - 44, gx + k * 26, gy + 44, GOLD, 1)
    cv.fill_rect(0, 152, W, 4, GOLD)

    # Story cards: 2 columns x 3 rows.
    cw, ch, gap, mx = 480, 258, 16, 24
    for idx, (accent, kicker, headline, deck, icon, source) in enumerate(STORIES):
        x = mx + (idx % 2) * (cw + gap)
        y = 172 + (idx // 2) * (ch + gap)
        cv.fill_rect(x, y, cw, ch, WHITE)
        cv.fill_rect(x, y, cw, ch, BORDER)  # border via outline below
        cv.fill_rect(x + 1, y + 1, cw - 2, ch - 2, WHITE)
        cv.fill_rect(x, y, cw, 6, accent)
        draw_icon(cv, x + 50, y + 50, icon, accent)
        draw_text(cv, x + 94, y + 40, kicker, 2, accent)
        draw_text(cv, x + 94, y + 62, "26 NOV 2026", 1, GREY)
        lines = wrap(headline, cw - 48, 3)
        for i, ln in enumerate(lines[:2]):
            draw_text(cv, x + 24, y + 96 + i * 28, ln, 3, INK)
        dlines = wrap(deck, cw - 48, 2)
        for i, ln in enumerate(dlines[:3]):
            draw_text(cv, x + 24, y + 162 + i * 20, ln, 2, GREY)
        draw_text(cv, x + 24, y + ch - 26, "SOURCE: " + source, 1, GREY)

    # Footer.
    foot = "SOURCES: AFP - REUTERS - INDIAN EXPRESS - MANILA TIMES"
    draw_text(cv, (W - text_width(foot, 2)) // 2, 996, foot, 2, GREY)
    return cv


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(render())
    if len(data) > 1048576:
        print(f"image too large: {len(data)} bytes", file=sys.stderr)
        return 1
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    # Round-trip check: what we wrote is a complete PNG of the right size.
    with open(path, "rb") as f:
        back = f.read()
    assert back == data and back[:8] == b"\x89PNG\r\n\x1a\n"
    assert back[-12:] == struct.pack(">I", 0) + b"IEND" + struct.pack(
        ">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    print(f"Wrote {len(data)} bytes to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
