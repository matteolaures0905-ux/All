#!/usr/bin/env python3
"""Lyric video cartoon v2 : decors colores et detailles, heros stylé qui interagit avec chaque scene.

  python3 cartoon2.py --lyrics paroles_a_remplir.json --audio son.m4a --duration 40.7 --out video.mp4
  python3 cartoon2.py ... --stills 1.5,5,9   -> planche d'apercu PNG au lieu de la video

Chaque ligne du JSON : start, end, text, scene (street|alley|park|room|stage|roof), action (voir ACTIONS).
"""
import argparse, json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_video import load_lyrics, audio_energy, bpm_energy  # noqa: E402
from make_cartoon import draw_lyrics  # noqa: E402

W, H = 1080, 1920
F_BOLD = os.path.join(HERE, "fonts", "oswald-latin-700-normal.woff")
INK = (24, 18, 32)
ACC = (247, 176, 49)
LW = 7

_fc = {}
def font(sz):
    if sz not in _fc:
        _fc[sz] = ImageFont.truetype(F_BOLD, sz)
    return _fc[sz]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def eob(x):
    x = clamp(x)
    return 1 + 3.2 * (x - 1) ** 3 + 2.2 * (x - 1) ** 2


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def shade(c, k):
    return tuple(int(clamp(v * k, 0, 255)) for v in c)


# ====================================================================== decors
def vgrad(img, stops, y0=0, y1=H):
    ys = np.linspace(0, 1, y1 - y0)
    arr = np.zeros((y1 - y0, 3))
    pos = [s[0] for s in stops]
    for c in range(3):
        arr[:, c] = np.interp(ys, pos, [s[1][c] for s in stops])
    img.paste(Image.fromarray(np.repeat(arr[:, None, :], W, 1).astype(np.uint8)), (0, y0))


def glow(img, x, y, r, col, alpha=120):
    lay = Image.new("RGBA", (int(r * 4), int(r * 4)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([r, r, r * 3, r * 3], fill=col + (alpha,))
    lay = lay.filter(ImageFilter.GaussianBlur(r * 0.5))
    img.alpha_composite(lay, (int(x - r * 2), int(y - r * 2)))


def neon(img, box, text, col):
    x0, y0, x1, y1 = box
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, 18, outline=col + (255,), width=8)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), text, font=font(int((y1 - y0) * 0.55)), fill=col + (255,), anchor="mm")
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
    img.alpha_composite(lay)
    d2 = ImageDraw.Draw(img)
    d2.text(((x0 + x1) / 2, (y0 + y1) / 2), text, font=font(int((y1 - y0) * 0.55)), fill=(255, 255, 255), anchor="mm")


def window_grid(d, x0, y0, x1, y1, rnd, lit_cols, dark, fw=46, fh=60, gx=30, gy=36):
    for wy in range(int(y0), int(y1) - fh, fh + gy):
        for wx in range(int(x0), int(x1) - fw, fw + gx):
            c = rnd.choice(lit_cols) if rnd.random() < 0.3 else dark
            d.rectangle([wx, wy, wx + fw, wy + fh], fill=c, outline=INK, width=4)
            d.line([wx + fw / 2, wy, wx + fw / 2, wy + fh], fill=INK, width=3)
            if c != dark:
                d.line([wx + 6, wy + 8, wx + 16, wy + 8], fill=(255, 255, 255), width=4)


def scene_street(rnd):
    img = Image.new("RGBA", (W, H))
    vgrad(img, [(0, (34, 14, 72)), (0.35, (110, 34, 120)), (0.62, (226, 82, 120)), (0.78, (255, 170, 110)), (1, (255, 200, 140))], 0, 1300)
    glow(img, 700, 930, 200, (255, 220, 150), 150)
    d = ImageDraw.Draw(img)
    d.ellipse([560, 790, 840, 1070], fill=(255, 224, 160))
    x = -40  # immeubles lointains
    while x < W:
        bw, bh = rnd.randint(90, 170), rnd.randint(250, 520)
        d.rectangle([x, 1100 - bh, x + bw, 1260], fill=(132, 52, 120))
        for wy in range(1100 - bh + 20, 1080, 44):
            for wx in range(x + 12, x + bw - 16, 30):
                if rnd.random() < 0.15:
                    d.rectangle([wx, wy, wx + 12, wy + 18], fill=(255, 196, 130))
        x += bw + 6
    x = -60  # immeubles proches
    cols = [(74, 40, 118), (96, 46, 132), (60, 34, 100), (110, 56, 146)]
    while x < W + 40:
        bw, bh = rnd.randint(220, 320), rnd.randint(620, 900)
        c = rnd.choice(cols)
        top = 1260 - bh
        d.rectangle([x, top, x + bw, 1270], fill=c, outline=INK, width=LW)
        d.rectangle([x + bw - 40, top + 4, x + bw - 4, 1266], fill=shade(c, 0.75))
        d.rectangle([x - 10, top - 26, x + bw + 10, top], fill=shade(c, 1.25), outline=INK, width=6)
        if rnd.random() < 0.6:  # clim / antenne
            d.rectangle([x + 30, top - 80, x + 110, top - 26], fill=(150, 150, 180), outline=INK, width=5)
            d.line([x + bw - 60, top - 26, x + bw - 60, top - 140], fill=INK, width=6)
            d.line([x + bw - 90, top - 110, x + bw - 30, top - 110], fill=INK, width=5)
        window_grid(d, x + 26, top + 40, x + bw - 40, 980, rnd, [(255, 205, 110), (110, 230, 230), (255, 150, 170)], (44, 26, 76))
        x += bw
    # devantures de boutiques
    awn = [((255, 92, 122), (255, 240, 230)), ((46, 190, 200), (240, 255, 250)), ((255, 190, 60), (255, 250, 230))]
    for i, sx in enumerate(range(-20, W, 370)):
        a, b = awn[i % 3]
        d.rectangle([sx + 20, 1040, sx + 340, 1270], fill=(40, 22, 60), outline=INK, width=LW)
        d.rectangle([sx + 50, 1110, sx + 310, 1250], fill=(255, 214, 140), outline=INK, width=5)
        for k in range(4):
            d.rectangle([sx + 70 + k * 60, 1190, sx + 110 + k * 60, 1250], fill=rnd.choice([(220, 80, 110), (60, 160, 190), (250, 170, 60)]), outline=INK, width=3)
        for k in range(8):
            d.polygon([(sx + 10 + k * 42, 1000), (sx + 52 + k * 42, 1000), (sx + 52 + k * 42, 1060), (sx + 10 + k * 42, 1060)], fill=a if k % 2 else b, outline=INK)
        for k in range(8):
            d.chord([sx + 10 + k * 42, 1040, sx + 52 + k * 42, 1080], 0, 180, fill=a if k % 2 else b, outline=INK, width=3)
    neon(img, (90, 880, 330, 970), "SNACK", (255, 70, 150))
    neon(img, (760, 860, 1000, 950), "24/7", (60, 230, 240))
    d = ImageDraw.Draw(img)
    # trottoir
    vgrad(img, [(0, (120, 78, 150)), (1, (80, 50, 110))], 1270, H)
    d = ImageDraw.Draw(img)
    d.line([0, 1270, W, 1270], fill=INK, width=LW)
    for y in (1360, 1480, 1640, 1830):
        d.line([0, y, W, y], fill=(70, 44, 98), width=4)
    for lx in range(-400, W + 400, 200):
        d.line([W / 2 + (lx - W / 2) * 0.35, 1270, lx, H], fill=(70, 44, 98), width=4)
    for px, py, pw in ((180, 1800, 220), (820, 1760, 180)):  # flaques
        d.ellipse([px - pw, py - 30, px + pw, py + 30], fill=(170, 120, 190))
        d.line([px - pw * 0.5, py - 6, px + pw * 0.2, py - 6], fill=(240, 200, 230), width=5)
    # lampadaire
    d.rectangle([985, 760, 1005, 1700], fill=(40, 30, 60), outline=INK, width=4)
    d.line([995, 770, 920, 770], fill=INK, width=12)
    glow(img, 920, 800, 90, (255, 220, 140), 180)
    d = ImageDraw.Draw(img)
    d.chord([870, 770, 970, 830], 0, 180, fill=(255, 230, 160), outline=INK, width=5)
    # bouche d'incendie
    d.rounded_rectangle([60, 1560, 120, 1690], 16, fill=(230, 60, 70), outline=INK, width=6)
    d.rectangle([40, 1590, 140, 1615], fill=(200, 40, 55), outline=INK, width=5)
    d.ellipse([70, 1535, 110, 1575], fill=(230, 60, 70), outline=INK, width=5)
    return img


def scene_alley(rnd):
    img = Image.new("RGBA", (W, H), (60, 28, 34))
    d = ImageDraw.Draw(img)
    bh, bw = 64, 150
    bricks = [(168, 69, 58), (142, 58, 51), (194, 91, 69), (156, 64, 60), (178, 80, 62)]
    for row, y in enumerate(range(0, 1380, bh)):
        off = (row % 2) * bw // 2
        for x in range(-bw, W + bw, bw):
            c = rnd.choice(bricks)
            d.rectangle([x + off + 4, y + 4, x + off + bw - 4, y + bh - 4], fill=c)
            d.line([x + off + 8, y + 10, x + off + bw - 30, y + 10], fill=shade(c, 1.18), width=4)
    # graffiti : grosses lettres-bulles abstraites
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(lay)
    gcols = [(50, 220, 210), (255, 210, 60), (190, 90, 255), (255, 90, 160)]
    for i in range(7):
        cx, cy = 120 + i * 140 + rnd.randint(-20, 20), 760 + rnd.randint(-80, 80)
        c = gcols[i % 4]
        r1, r2 = rnd.randint(70, 110), rnd.randint(90, 150)
        gd.rounded_rectangle([cx - r1, cy - r2, cx + r1, cy + r2], 60, fill=c + (235,), outline=INK + (255,), width=9)
        gd.ellipse([cx - r1 * 0.4, cy - r2 * 0.6, cx + r1 * 0.1, cy - r2 * 0.1], fill=(255, 255, 255, 200))
        for k in range(2):  # coulures
            dx = rnd.randint(-r1 + 20, r1 - 20)
            ln = rnd.randint(40, 140)
            gd.line([cx + dx, cy + r2 - 10, cx + dx, cy + r2 + ln], fill=c + (235,), width=12)
            gd.ellipse([cx + dx - 9, cy + r2 + ln - 6, cx + dx + 9, cy + r2 + ln + 12], fill=c + (235,))
    gd.text((540, 560), "WAVE", font=font(170), fill=(255, 255, 255, 230), anchor="mm", stroke_width=10, stroke_fill=INK + (255,))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    # tuyau + clim + affiche dechiree
    d.rectangle([40, 0, 90, 1400], fill=(110, 120, 140), outline=INK, width=6)
    for y in range(120, 1400, 260):
        d.rectangle([28, y, 102, y + 34], fill=(140, 150, 170), outline=INK, width=5)
    d.rectangle([790, 980, 1020, 1160], fill=(200, 205, 215), outline=INK, width=LW)
    d.ellipse([815, 1000, 955, 1140], fill=(150, 155, 170), outline=INK, width=5)
    for a in range(0, 360, 60):
        r = math.radians(a)
        d.line([885, 1070, 885 + 60 * math.cos(r), 1070 + 60 * math.sin(r)], fill=INK, width=5)
    d.polygon([(150, 1000), (330, 990), (340, 1180), (250, 1160), (160, 1190)], fill=(250, 240, 220), outline=INK)
    d.rectangle([180, 1020, 310, 1080], fill=(255, 90, 160))
    for y in (1100, 1125, 1150):
        d.line([180, y, 300, y], fill=(120, 110, 120), width=6)
    # sol
    vgrad(img, [(0, (70, 60, 96)), (1, (40, 34, 60))], 1380, H)
    d = ImageDraw.Draw(img)
    d.rectangle([-10, 1370, W + 10, 1400], fill=(90, 80, 116), outline=INK, width=6)
    d.ellipse([560, 1780, 980, 1850], fill=(100, 90, 140))
    for bx in (150, 250):  # sacs poubelle
        d.ellipse([bx - 80, 1500, bx + 80, 1680], fill=(40, 60, 50), outline=INK, width=LW)
        d.line([bx - 20, 1510, bx + 20, 1490], fill=INK, width=6)
    return img


def tree(d, x, y, r, rnd):
    d.polygon([(x - 26, y + r * 1.8), (x + 26, y + r * 1.8), (x + 14, y), (x - 14, y)], fill=(110, 70, 50), outline=INK)
    greens = [(47, 143, 107), (63, 178, 127), (36, 110, 85), (80, 190, 120)]
    for k in range(7):
        a = k / 7 * math.tau
        cx, cy = x + r * 0.6 * math.cos(a), y - r * 0.2 + r * 0.45 * math.sin(a)
        rr = r * rnd.uniform(0.5, 0.7)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=rnd.choice(greens[:3]), outline=INK, width=6)
    d.ellipse([x - r * 0.6, y - r * 0.8, x + r * 0.6, y + r * 0.3], fill=greens[1], outline=INK, width=6)
    d.arc([x - r * 0.45, y - r * 0.65, x + r * 0.3, y], 200, 280, fill=(150, 230, 170), width=10)


def scene_park(rnd):
    img = Image.new("RGBA", (W, H))
    vgrad(img, [(0, (60, 160, 190)), (0.5, (116, 211, 200)), (1, (255, 225, 168))], 0, 1250)
    d = ImageDraw.Draw(img)
    for cx, cy in ((220, 560), (780, 470), (560, 700)):  # nuages
        for dx, r in ((-70, 50), (0, 70), (70, 55)):
            d.ellipse([cx + dx - r, cy - r, cx + dx + r, cy + r], fill=(255, 255, 255))
        d.rectangle([cx - 120, cy, cx + 125, cy + 50], fill=(255, 255, 255))
    for cx in (200, 700):  # oiseaux
        d.arc([cx, 600, cx + 40, 630], 200, 340, fill=INK, width=5)
        d.arc([cx + 36, 600, cx + 76, 630], 200, 340, fill=INK, width=5)
    d.ellipse([-300, 1000, 700, 1500], fill=(90, 170, 140))
    d.ellipse([400, 980, 1400, 1500], fill=(70, 150, 125))
    for i, tx in enumerate((60, 330, 760, 1030)):
        tree(d, tx, 930 + (i % 2) * 40, 170, rnd)
    vgrad(img, [(0, (90, 180, 110)), (1, (60, 140, 90))], 1250, H)
    d = ImageDraw.Draw(img)
    d.line([0, 1250, W, 1250], fill=INK, width=LW)
    d.polygon([(380, 1250), (700, 1250), (980, H), (100, H)], fill=(232, 206, 160))
    d.line([(380, 1250), (100, H)], fill=(200, 170, 120), width=6)
    d.line([(700, 1250), (980, H)], fill=(200, 170, 120), width=6)
    for k in range(7):  # cloture
        x = 20 + k * 40
        d.rectangle([x, 1150, x + 22, 1300], fill=(250, 245, 235), outline=INK, width=4)
    d.line([0, 1190, 300, 1190], fill=INK, width=6)
    for _ in range(60):
        gx, gy = rnd.randint(0, W), rnd.randint(1270, H)
        if 100 < gx < 980 and gy > 1250 + (gx - 380) * 0:
            pass
        d.line([gx, gy, gx + 6, gy - 20], fill=(50, 120, 70), width=5)
    for _ in range(26):  # fleurs
        fx, fy = rnd.choice([rnd.randint(10, 260), rnd.randint(820, 1070)]), rnd.randint(1300, 1880)
        c = rnd.choice([(255, 110, 150), (255, 220, 80), (250, 250, 250), (180, 120, 255)])
        for a in range(0, 360, 72):
            r = math.radians(a)
            d.ellipse([fx + 11 * math.cos(r) - 8, fy + 11 * math.sin(r) - 8, fx + 11 * math.cos(r) + 8, fy + 11 * math.sin(r) + 8], fill=c)
        d.ellipse([fx - 6, fy - 6, fx + 6, fy + 6], fill=ACC)
    for bx, by in ((40, 1260), (900, 1240)):  # buissons
        for dx, r in ((0, 70), (80, 90), (170, 65)):
            d.ellipse([bx + dx - r, by - r, bx + dx + r, by + r * 0.7], fill=(45, 130, 90), outline=INK, width=6)
    # banc
    wood = (186, 116, 64)
    for y in (1270, 1310):
        d.rounded_rectangle([560, y, 1060, y + 30], 8, fill=wood, outline=INK, width=6)
    d.rounded_rectangle([540, 1370, 1080, 1410], 8, fill=shade(wood, 1.1), outline=INK, width=6)
    for lx in (580, 1040):
        d.rectangle([lx - 10, 1410, lx + 10, 1500], fill=INK)
    # lampadaire
    d.rectangle([505, 760, 520, 1300], fill=(40, 50, 60), outline=INK, width=4)
    d.ellipse([480, 720, 545, 780], fill=(255, 235, 170), outline=INK, width=6)
    return img


def scene_room(rnd):
    img = Image.new("RGBA", (W, H), (31, 78, 95))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 90):
        d.rectangle([x, 0, x + 45, 1380], fill=(36, 88, 106))
    # fenetre sur la ville la nuit
    wx0, wy0, wx1, wy1 = 90, 560, 470, 1060
    vgrad(img, [(0, (20, 24, 70)), (1, (90, 50, 120))], wy0, wy1)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, wx0, H], fill=None)
    img2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rectangle([wx0, wy0, wx1, wy1], fill=255)
    base = Image.new("RGBA", (W, H), (31, 78, 95))
    vgrad(base, [(0, (20, 24, 70)), (1, (110, 60, 130))], 0, H)
    bd = ImageDraw.Draw(base)
    bd.ellipse([340, 600, 420, 680], fill=(250, 240, 210))
    x = wx0
    while x < wx1:
        bw, bh = rnd.randint(40, 90), rnd.randint(120, 330)
        bd.rectangle([x, wy1 - bh, x + bw, wy1], fill=(30, 26, 60))
        for wy in range(wy1 - bh + 12, wy1 - 10, 26):
            for wxx in range(x + 8, x + bw - 10, 18):
                if rnd.random() < 0.35:
                    bd.rectangle([wxx, wy, wxx + 8, wy + 12], fill=rnd.choice([(255, 210, 110), (120, 230, 240), (255, 120, 170)]))
        x += bw
    img.paste(base, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.rectangle([wx0, wy0, wx1, wy1], outline=INK, width=12)
    d.line([(wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1], fill=INK, width=10)
    d.line([wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2], fill=INK, width=10)
    for cx0 in (wx0 - 60, wx1 - 20):  # rideaux
        d.polygon([(cx0, wy0 - 40), (cx0 + 80, wy0 - 40), (cx0 + 60, wy1 + 60), (cx0 + 10, wy1 + 60)], fill=(232, 120, 70), outline=INK)
        d.line([cx0 + 40, wy0 - 30, cx0 + 36, wy1 + 50], fill=(200, 90, 50), width=6)
    d.rectangle([wx0 - 80, wy0 - 60, wx1 + 80, wy0 - 40], fill=(120, 80, 50), outline=INK, width=5)
    # etagere + livres + plante
    d.rectangle([640, 760, 1000, 790], fill=(160, 100, 60), outline=INK, width=6)
    x = 660
    for _ in range(9):
        bw, bh = rnd.randint(22, 40), rnd.randint(90, 140)
        d.rectangle([x, 790 - bh, x + bw, 790], fill=rnd.choice([(230, 90, 90), (250, 200, 80), (90, 180, 200), (180, 120, 240), (240, 240, 230)]), outline=INK, width=4)
        x += bw + 2
    d.polygon([(900, 790), (980, 790), (965, 700), (915, 700)], fill=(230, 120, 70), outline=INK)
    for a in (-60, -30, 0, 30, 60):
        r = math.radians(a - 90)
        d.ellipse([940 + 70 * math.cos(r) - 22, 690 + 70 * math.sin(r) - 40, 940 + 70 * math.cos(r) + 22, 690 + 70 * math.sin(r) + 40], fill=(60, 170, 110), outline=INK, width=4)
    # cadre photo (amis)
    d.rectangle([640, 880, 900, 1080], fill=ACC, outline=INK, width=LW)
    d.rectangle([665, 905, 875, 1055], fill=(250, 220, 190), outline=INK, width=4)
    for fx, c in ((730, (90, 170, 100)), (810, (28, 110, 140))):
        d.ellipse([fx - 30, 935, fx + 30, 995], fill=(160, 110, 80), outline=INK, width=4)
        d.chord([fx - 50, 990, fx + 50, 1090], 180, 360, fill=c, outline=INK, width=4)
    # sol parquet + tapis
    d.rectangle([-10, 1380, W + 10, H + 10], fill=(138, 90, 59))
    for y in range(1380, H, 70):
        d.line([0, y, W, y], fill=(110, 70, 45), width=4)
        off = (y // 70) % 2 * 120
        for x in range(off, W, 240):
            d.line([x, y, x, y + 70], fill=(110, 70, 45), width=4)
    d.line([0, 1380, W, 1380], fill=INK, width=LW)
    d.rectangle([-10, 1360, W + 10, 1385], fill=(240, 230, 210), outline=INK, width=5)
    d.ellipse([60, 1620, 1020, 1860], fill=(190, 64, 78), outline=INK, width=6)
    d.ellipse([160, 1660, 920, 1820], outline=(240, 180, 90), width=8)
    return img


def scene_stage(rnd):
    img = Image.new("RGBA", (W, H), (42, 15, 28))
    d = ImageDraw.Draw(img)
    d.rectangle([150, 420, 930, 1420], fill=(70, 26, 48))
    for i in range(20):  # etoiles du decor
        x, y = rnd.randint(200, 880), rnd.randint(480, 1300)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 220, 160))
    reds = [(142, 27, 46), (180, 42, 60), (110, 20, 36)]
    for side in (0, 1):  # rideaux
        for k in range(6):
            x0 = k * 40 if side == 0 else W - (k + 1) * 40
            d.rectangle([x0, 380, x0 + 40, 1560], fill=reds[k % 3])
        d.line([(240 if side == 0 else W - 240), 380, (240 if side == 0 else W - 240), 1560], fill=INK, width=6)
    d.rectangle([-10, 340, W + 10, 470], fill=reds[0])
    for x in range(0, W + 60, 60):
        d.chord([x - 30, 430, x + 30, 510], 0, 180, fill=reds[1], outline=INK, width=4)
        d.line([x, 470, x, 520], fill=ACC, width=4)
        d.ellipse([x - 8, 515, x + 8, 535], fill=ACC)
    d.line([0, 470, W, 470], fill=ACC, width=10)
    # rampe de spots
    d.rectangle([-10, 360, W + 10, 384], fill=(60, 60, 70), outline=INK, width=5)
    for x in range(120, W, 210):
        d.polygon([(x - 34, 384), (x + 34, 384), (x + 24, 440), (x - 24, 440)], fill=(40, 40, 50), outline=INK)
        d.ellipse([x - 22, 430, x + 22, 450], fill=ACC)
    # enceintes
    for sx in (60, W - 200):
        d.rectangle([sx, 1180, sx + 140, 1420], fill=(30, 26, 36), outline=INK, width=LW)
        d.ellipse([sx + 30, 1220, sx + 110, 1300], fill=(60, 56, 70), outline=INK, width=5)
        d.ellipse([sx + 20, 1310, sx + 120, 1410], fill=(60, 56, 70), outline=INK, width=5)
    # plancher
    d.rectangle([-10, 1420, W + 10, 1560], fill=(160, 98, 58))
    for x in range(0, W, 90):
        d.line([x, 1420, x - 20, 1560], fill=(130, 78, 46), width=4)
    d.line([0, 1420, W, 1420], fill=INK, width=LW)
    d.rectangle([-10, 1560, W + 10, 1600], fill=(110, 60, 36), outline=INK, width=6)
    for x in range(40, W, 110):
        d.ellipse([x - 12, 1566, x + 12, 1590], fill=(255, 230, 150))
    d.rectangle([-10, 1600, W + 10, H + 10], fill=(30, 12, 22))
    return img


def scene_roof(rnd):
    img = Image.new("RGBA", (W, H))
    vgrad(img, [(0, (13, 27, 61)), (0.55, (59, 42, 107)), (0.85, (150, 70, 130)), (1, (220, 110, 120))], 0, 1260)
    d = ImageDraw.Draw(img)
    for _ in range(90):
        x, y = rnd.randint(0, W), rnd.randint(380, 1000)
        r = rnd.choice([2, 2, 3, 4])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 230))
    glow(img, 800, 560, 110, (255, 240, 200), 110)
    d = ImageDraw.Draw(img)
    d.ellipse([720, 480, 880, 640], fill=(255, 246, 220), outline=INK, width=6)
    d.ellipse([760, 520, 795, 555], fill=(235, 220, 190)); d.ellipse([820, 580, 845, 605], fill=(235, 220, 190))
    x = -30
    while x < W:
        bw, bh = rnd.randint(80, 180), rnd.randint(150, 420)
        d.rectangle([x, 1200 - bh, x + bw, 1210], fill=(30, 28, 68))
        for wy in range(1215 - bh, 1180, 40):
            for wx in range(x + 14, x + bw - 18, 30):
                if rnd.random() < 0.3:
                    d.rectangle([wx, wy, wx + 14, wy + 20], fill=rnd.choice([(255, 210, 110), (120, 230, 240), (255, 120, 190)]))
        x += bw
    # chateau d'eau
    d.rectangle([110, 900, 300, 1110], fill=(140, 86, 56), outline=INK, width=LW)
    for y in (950, 1010, 1070):
        d.line([110, y, 300, y], fill=(110, 66, 40), width=6)
    d.polygon([(100, 900), (310, 900), (205, 820)], fill=(110, 66, 40), outline=INK)
    for lx in (130, 280):
        d.line([lx, 1110, lx, 1230], fill=INK, width=12)
    # toit
    vgrad(img, [(0, (70, 76, 112)), (1, (44, 46, 78))], 1220, H)
    d = ImageDraw.Draw(img)
    d.rectangle([-10, 1200, W + 10, 1240], fill=(100, 106, 150), outline=INK, width=6)
    d.rectangle([860, 1080, 960, 1220], fill=(120, 126, 160), outline=INK, width=6)
    d.rectangle([850, 1060, 970, 1090], fill=(140, 146, 180), outline=INK, width=6)
    # guirlande lumineuse
    pts = [(x, 420 + 60 * math.sin(x / W * math.pi)) for x in range(0, W + 1, 20)]
    d.line(pts, fill=INK, width=4)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i, (x, y) in enumerate(pts[1::3]):
        c = [(255, 210, 90), (255, 100, 160), (90, 230, 240), (160, 255, 140)][i % 4]
        ld.ellipse([x - 18, y - 6, x + 18, y + 30], fill=c + (140,))
        d.ellipse([x - 8, y + 2, x + 8, y + 22], fill=c, outline=INK, width=3)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))
    return img


SCENES = {"street": (scene_street, 1700), "alley": (scene_alley, 1680), "park": (scene_park, 1660),
          "room": (scene_room, 1720), "stage": (scene_stage, 1540), "roof": (scene_roof, 1660)}
TOP_TINT = {"street": (24, 10, 52), "alley": (40, 16, 22), "park": (22, 70, 90), "room": (16, 44, 56),
            "stage": (30, 8, 18), "roof": (10, 18, 44)}


# ====================================================================== personnages
HERO = dict(skin=(141, 90, 59), skin_d=(112, 68, 42), jacket=(28, 110, 140), jacket_d=(18, 82, 106),
            sleeve=(242, 230, 207), sleeve_d=(214, 200, 176), cuff=(255, 122, 61), pants=(34, 32, 48),
            shoe=(250, 250, 250), sole=(190, 190, 205), shoe_acc=(255, 122, 61), hat="cap_back", glow=(255, 176, 20),
            hat_col=(255, 122, 61), hair=(26, 20, 16), chain=True, patch=True, tee=(250, 250, 250))
HERO_DARK = dict(skin=(128, 80, 52), skin_d=(92, 56, 36), jacket=(26, 26, 32), jacket_d=(12, 12, 16),
                 sleeve=(26, 26, 32), sleeve_d=(12, 12, 16), cuff=(18, 18, 22), pants=(18, 18, 24),
                 shoe=(30, 30, 36), sole=(60, 60, 70), shoe_acc=(255, 176, 20), hat="cap_back", glow=(255, 176, 20),
                 hat_col=(34, 34, 42), hair=(16, 12, 10), chain=True, patch=True, tee=(20, 20, 24),
                 puffer=True, gloss=(105, 110, 135), brooding=True)
FRIEND = dict(skin=(224, 172, 130), skin_d=(196, 140, 100), jacket=(80, 170, 90), jacket_d=(58, 136, 70),
              sleeve=(80, 170, 90), sleeve_d=(58, 136, 70), cuff=(58, 136, 70), pants=(70, 80, 120),
              shoe=(40, 40, 50), sole=(230, 230, 230), shoe_acc=(250, 250, 250), hat="curly",
              hat_col=(70, 44, 30), hair=(70, 44, 30), chain=False, patch=False, tee=(240, 240, 240))


def random_style(rnd):
    j = rnd.choice([(200, 70, 90), (110, 90, 200), (230, 170, 60), (60, 150, 170), (150, 150, 165), (200, 110, 160)])
    sk = rnd.choice([((241, 194, 155), (210, 160, 120)), ((198, 134, 92), (166, 104, 66)), ((110, 70, 48), (86, 52, 34)), ((232, 182, 140), (200, 146, 106))])
    hat = rnd.choice(["cap", "afro", "bun", "short", "curly"])
    hair = rnd.choice([(30, 22, 18), (90, 56, 30), (200, 150, 70), (20, 20, 24)])
    return dict(skin=sk[0], skin_d=sk[1], jacket=j, jacket_d=shade(j, 0.78), sleeve=j, sleeve_d=shade(j, 0.78),
                cuff=shade(j, 0.7), pants=rnd.choice([(40, 40, 60), (70, 90, 140), (90, 80, 70)]),
                shoe=rnd.choice([(250, 250, 250), (40, 40, 50)]), sole=(220, 220, 230), shoe_acc=shade(j, 0.9),
                hat=hat, hat_col=rnd.choice([(40, 40, 60), (220, 60, 70), (60, 120, 200)]), hair=hair,
                chain=False, patch=False, tee=(240, 240, 240))


def ik(sx, sy, tx, ty, l1, l2, bend):
    dx, dy = tx - sx, ty - sy
    dist = clamp(math.hypot(dx, dy), abs(l1 - l2) + 1, l1 + l2 - 1)
    a = math.atan2(dy, dx)
    A = math.acos(clamp((l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist), -1, 1))
    ex, ey = sx + l1 * math.cos(a + bend * A), sy + l1 * math.sin(a + bend * A)
    hx, hy = sx + (l1 + l2) * 0 + dist * math.cos(a), sy + dist * math.sin(a)
    return ex, ey, hx, hy


def soft_shadow(frame, cx, gy, w):
    lay = Image.new("RGBA", (int(w * 2.6), 120), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([w * 0.3, 30, w * 2.3, 90], fill=(0, 0, 0, 90))
    frame.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)), (int(cx - w * 1.3), int(gy - 60)))


def draw_person(frame, cx, gy, t, st, pose, s=1.0, phase=0.0):
    """Dessine un personnage. pose : dict (voir default_pose)."""
    soft_shadow(frame, cx, gy, 150 * s)
    d = ImageDraw.Draw(frame)
    bob = (6 * math.sin(t * 6 + phase) + pose.get("bob", 0)) * s
    def P(x, y):
        return (cx + x * s, gy + y * s + (bob if y < -240 else 0))
    def S(v):
        return max(1, int(v * s))
    lw = S(LW)
    # ---- jambes
    walk = pose.get("walk", 0)
    tap = pose.get("tap", 0)
    for side in (-1, 1):
        sw = math.sin(t * 9 + phase) * 34 * side * walk
        lift = max(0, math.sin(t * 9 + phase) * side) * 26 * walk + (tap if side == 1 else 0)
        hip = P(42 * side, -270)
        foot = P(42 * side + sw, -40 - lift)
        d.line([hip, foot], fill=INK, width=S(84))
        d.line([hip, foot], fill=st["pants"], width=S(70))
        fx, fy = foot
        d.rounded_rectangle([fx - S(10), fy - S(70), fx + S(10), fy - S(30)], S(4), fill=shade(st["pants"], 0.8))
        # basket
        d.rounded_rectangle([fx - S(56), fy - S(26), fx + S(62), fy + S(32)], S(26), fill=st["shoe"], outline=INK, width=lw)
        d.rounded_rectangle([fx - S(60), fy + S(14), fx + S(66), fy + S(42)], S(12), fill=st["sole"], outline=INK, width=S(5))
        d.line([fx - S(30), fy, fx + S(30), fy - S(10)], fill=st["shoe_acc"], width=S(10))
    # ---- buste
    x0, y0 = P(-122, -575); x1, y1 = P(122, -248)
    if st.get("puffer"):
        draw_puffer_torso(d, P, S, st, lw)
    else:
        d.rounded_rectangle([x0, y0, x1, y1], S(64), fill=st["jacket"], outline=INK, width=lw)
        d.rounded_rectangle([P(60, -560)[0], P(60, -560)[1], P(112, -262)[0], P(112, -262)[1]], S(40), fill=st["jacket_d"])
        d.rounded_rectangle([x0, y0, x1, y1], S(64), outline=INK, width=lw)
        d.rounded_rectangle([*P(-118, -290), *P(118, -248)], S(18), fill=st["cuff"], outline=INK, width=S(5))
        d.line([P(-110, -270), P(110, -270)], fill=shade(st["cuff"], 0.75), width=S(5))
        d.chord([*P(-58, -600), *P(58, -500)], 0, 180, fill=st["tee"], outline=INK, width=S(5))
        d.line([P(0, -505), P(0, -290)], fill=INK, width=S(5))
    if st.get("patch") and not st.get("puffer"):
        px, py = P(-62, -440)
        pts = [(px + S(34) * math.cos(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45),
                py + S(34) * math.sin(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45)) for i in range(10)]
        d.polygon(pts, fill=ACC, outline=INK)
        d.rounded_rectangle([*P(30, -370), *P(95, -330)], S(8), fill=st["jacket_d"], outline=INK, width=S(4))
    if st.get("puffer"):
        pass
    if st.get("chain"):
        cyc = -545 if st.get("puffer") else -560
        pts = [P(52 * math.cos(a), cyc + 66 * math.sin(a)) for a in np.linspace(0.15, math.pi - 0.15, 14)]
        for (px, py) in pts:
            d.ellipse([px - S(7), py - S(7), px + S(7), py + S(7)], fill=ACC, outline=INK, width=S(2))
        px, py = P(0, -478 + (15 if st.get("puffer") else 0))
        d.ellipse([px - S(20), py - S(20), px + S(20), py + S(20)], fill=ACC, outline=INK, width=S(4))
        d.ellipse([px - S(8), py - S(8), px + S(8), py + S(8)], fill=(255, 240, 180))
    # ---- tete
    hood = pose.get("hood")
    if st["hat"] == "long" and not hood:  # cheveux longs derriere la tete
        sway = 6 * math.sin(t * 3 + phase)
        d.rounded_rectangle([*P(-140, -860), *P(140, -700)], S(70), fill=st["hair"], outline=INK, width=lw)
        for k in (-1, 1):  # deux meches qui tombent sur les epaules
            x0 = 78 if k == 1 else -150
            d.rounded_rectangle([*P(x0 + sway, -800), *P(x0 + 72 + sway, -455)], S(34), fill=st["hair"], outline=INK, width=lw)
            d.line([P(x0 + 30 + sway, -700), P(x0 + 30 + sway, -490)], fill=shade(st["hair"], 1.4), width=S(6))
    if hood:
        d.ellipse([*P(-150, -870), *P(150, -560)], fill=st["jacket"], outline=INK, width=lw)
    d.rectangle([*P(-30, -610), *P(30, -560)], fill=st["skin_d"])
    for k in (-1, 1):
        ex_, ey_ = P(112 * k, -690)
        d.ellipse([ex_ - S(22), ey_ - S(28), ex_ + S(22), ey_ + S(28)], fill=st["skin"], outline=INK, width=S(5))
    d.ellipse([*P(-112, -830), *P(112, -585)], fill=st["skin"], outline=INK, width=lw)
    d.chord([*P(-112, -830), *P(112, -585)], 20, 160, fill=st["skin"])
    if st.get("brooding"):
        d.chord([*P(-108, -826), *P(108, -590)], 195, 345, fill=st["skin_d"])
    d.arc([*P(-112, -830), *P(112, -585)], 0, 360, fill=INK, width=lw)
    hat = "hood" if hood else st["hat"]
    if hat == "beanie":
        d.chord([*P(-118, -900), *P(118, -700)], 180, 360, fill=st["hat_col"], outline=INK, width=lw)
        d.rounded_rectangle([*P(-124, -812), *P(124, -760)], S(20), fill=shade(st["hat_col"], 0.85), outline=INK, width=lw)
        for x in range(-100, 101, 28):
            d.line([P(x, -806), P(x, -766)], fill=shade(st["hat_col"], 0.65), width=S(4))
        d.rounded_rectangle([*P(50, -805), *P(96, -772)], S(5), fill=(250, 250, 250), outline=INK, width=S(3))
    elif hat == "cap_back":
        draw_cap_back(frame, P(0, -826), s, st["hat_col"], st["hair"], t)
        d = ImageDraw.Draw(frame)
    elif hat == "cap":
        d.chord([*P(-114, -900), *P(114, -720)], 180, 360, fill=st["hat_col"], outline=INK, width=lw)
        d.rounded_rectangle([*P(-30, -830), *P(170, -795)], S(16), fill=shade(st["hat_col"], 0.8), outline=INK, width=lw)
    elif hat == "afro":
        for a in range(200, 341, 20):
            r = math.radians(a)
            hx_, hy_ = P(100 * math.cos(r), -735 + 90 * math.sin(r))
            d.ellipse([hx_ - S(50), hy_ - S(50), hx_ + S(50), hy_ + S(50)], fill=st["hair"], outline=INK, width=S(5))
        d.chord([*P(-112, -870), *P(112, -660)], 180, 360, fill=st["hair"])
    elif hat == "bun":
        d.ellipse([*P(-40, -900), *P(40, -820)], fill=st["hair"], outline=INK, width=S(5))
        d.chord([*P(-114, -850), *P(114, -690)], 180, 360, fill=st["hair"], outline=INK, width=lw)
    elif hat == "curly":
        for x in range(-100, 101, 40):
            hx_, hy_ = P(x, -790 - (60 - abs(x) * 0.4))
            d.ellipse([hx_ - S(34), hy_ - S(34), hx_ + S(34), hy_ + S(34)], fill=st["hair"], outline=INK, width=S(4))
        d.chord([*P(-112, -840), *P(112, -700)], 180, 360, fill=st["hair"])
    elif hat == "long":
        d.chord([*P(-120, -860), *P(120, -660)], 180, 360, fill=st["hair"], outline=INK, width=lw)
        d.pieslice([*P(-130, -830), *P(40, -680)], 180, 270, fill=st["hair"])   # meche sur le cote
        d.arc([*P(-90, -850), *P(30, -720)], 200, 260, fill=shade(st["hair"], 1.4), width=S(8))
    elif hat == "short":
        d.chord([*P(-114, -840), *P(114, -700)], 180, 360, fill=st["hair"], outline=INK, width=lw)
    elif hat == "hood":
        d.arc([*P(-128, -860), *P(128, -600)], 180, 360, fill=shade(st["jacket"], 0.8), width=S(26))
    # yeux
    lx, ly = pose.get("look", (0, 0))
    blink = ((t + phase * 1.3) % 3.4) < 0.12 or pose.get("eyes") == "closed"
    sleepy = pose.get("eyes") == "sleepy"
    glows = []
    if st.get("glow") and not blink and pose.get("shades", 0) < 0.9:
        gc = st["glow"]
        pulse = 0.75 + 0.25 * VOC[0]
        for k in (-1, 1):
            gx_, gy_ = P(40 * k, -695)
            for rad, al, bl in ((S(95), int(80 * pulse), 0.45), (S(55), int(190 * pulse), 0.3)):
                lay = Image.new("RGBA", (rad * 4, rad * 4), (0, 0, 0, 0))
                ImageDraw.Draw(lay).ellipse([rad * 1.1, rad * 1.5, rad * 2.9, rad * 2.5], fill=gc + (al,))
                frame.alpha_composite(lay.filter(ImageFilter.GaussianBlur(rad * bl)), (int(gx_ - rad * 2), int(gy_ - rad * 2)))
        d = ImageDraw.Draw(frame)
    for k in (-1, 1):
        ex_, ey_ = P(40 * k, -695)
        if blink:
            d.arc([ex_ - S(22), ey_ - S(16), ex_ + S(22), ey_ + S(12)], 20, 160, fill=st.get("glow", INK), width=S(7))
            continue
        if st.get("glow"):
            gc = st["glow"]
            glows.append((ex_, ey_))
            # amande inclinee : coin exterieur releve
            def almond(rx, ry):
                pts = []
                for i in range(25):
                    u = i / 24
                    x = -rx + 2 * rx * u
                    pts.append((x, -ry * math.sin(math.pi * u)))
                for i in range(25):
                    u = 1 - i / 24
                    x = -rx + 2 * rx * u
                    pts.append((x, ry * 0.75 * math.sin(math.pi * u)))
                tilt = math.radians(-14 * k)
                return [(ex_ + s * (x * math.cos(tilt) - y * math.sin(tilt)), ey_ + s * (x * math.sin(tilt) + y * math.cos(tilt))) for x, y in pts]
            outer = almond(38, 26)
            d.polygon(outer, fill=INK)
            d.polygon(almond(35, 23), fill=mix(gc, (255, 255, 255), 0.2))   # liseré neon
            d.polygon(almond(31, 20), fill=gc)
            d.polygon(almond(24, 15), fill=mix(gc, (255, 250, 200), 0.55))
            d.polygon(almond(14, 9), fill=(255, 252, 225))                    # coeur presque blanc
            # pupille fendue verticale (s'elargit un peu quand il est surpris)
            px_, py_ = ex_ + lx * S(9), ey_ + ly * S(4)
            pw = S(5 + (5 if pose.get("brows") == "up" else 0))
            d.ellipse([px_ - pw, py_ - S(21), px_ + pw, py_ + S(17)], fill=(10, 8, 16))
            d.ellipse([px_ + S(7), py_ - S(14), px_ + S(13), py_ - S(7)], fill=(255, 255, 255))
            d.line(outer[:25], fill=INK, width=S(7))
            if sleepy:  # paupiere a moitie fermee
                lid = almond(40, 28)[:25]
                mid = [(x, y + (ey_ - y) * 0.45) for x, y in almond(38, 26)[:25]]
                d.polygon(lid + mid[::-1], fill=st["skin"])
                d.line(mid, fill=INK, width=S(7))
            continue
        d.ellipse([ex_ - S(24), ey_ - S(28), ex_ + S(24), ey_ + S(28)], fill=(255, 255, 255), outline=INK, width=S(5))
        px_, py_ = ex_ + lx * S(9), ey_ + ly * S(10)
        d.ellipse([px_ - S(13), py_ - S(14), px_ + S(13), py_ + S(14)], fill=INK)
        d.ellipse([px_ - S(4), py_ - S(10), px_ + S(3), py_ - S(3)], fill=(255, 255, 255))
        if sleepy:
            d.chord([ex_ - S(26), ey_ - S(30), ex_ + S(26), ey_ + S(26)], 180, 360, fill=st["skin"], outline=INK, width=S(5))
    # sourcils
    brows = pose.get("brows", "angry" if st.get("brooding") else "neutral")
    if st.get("brooding") and brows == "neutral":
        brows = "angry"
    for k in (-1, 1):
        bx, by = P(40 * k, -745)
        inner, outer = 0, 0
        if brows == "angry":
            inner, outer = 12, -6
        elif brows == "up":
            inner, outer = -14, -10
        elif brows == "sad":
            inner, outer = -12, 8
        elif brows == "skeptic":
            inner, outer = (-16, -16) if k == 1 else (6, 2)
        d.line([bx - S(26) * k * -1 * -1 * (1 if k == 1 else 1) - S(26) * (k < 0) * 0, by, bx, by], fill=INK, width=1)
        a = (bx - S(26) * k, by + S(outer)) if k == 1 else (bx - S(26) * k, by + S(outer))
        b = (bx + S(4) * -k, by + S(inner))
        d.line([(bx + S(28) * k, by + S(outer)), (bx - S(20) * k, by + S(inner))], fill=st["hair"] if st["hair"] != INK else INK, width=S(11))
    if st.get("earrings"):
        for k in (-1, 1):
            ex_, ey_ = P(114 * k, -650)
            d.ellipse([ex_ - S(16), ey_ - S(4), ex_ + S(16), ey_ + S(30)], outline=ACC, width=S(6))
    if st.get("lashes") and not blink:
        for k in (-1, 1):
            ex_, ey_ = P(40 * k, -695)
            d.line([ex_ + S(22) * k, ey_ - S(20), ex_ + S(36) * k, ey_ - S(30)], fill=INK, width=S(6))
    # nez
    nx, ny = P(0, -660)
    d.arc([nx - S(14), ny - S(12), nx + S(14), ny + S(12)], 20, 160, fill=st["skin_d"], width=S(6))
    # bouche
    mx, my = P(0, -622)
    m = pose.get("mouth", "smirk")
    talk = pose.get("talk", 0)
    if talk > 0.18 and m not in ("o",):
        h = S(10 + 40 * talk)
        d.rounded_rectangle([mx - S(30), my - h / 2, mx + S(30), my + h / 2], S(16), fill=(110, 30, 40), outline=INK, width=S(5))
        d.rectangle([mx - S(22), my - h / 2 + S(4), mx + S(22), my - h / 2 + S(11)], fill=(255, 255, 255))
        if h > S(28):
            d.chord([mx - S(18), my, mx + S(18), my + h / 2 - S(2)], 180, 360, fill=(230, 100, 110))
    elif m == "smile":
        d.chord([mx - S(36), my - S(26), mx + S(36), my + S(22)], 0, 180, fill=(110, 30, 40), outline=INK, width=S(5))
        d.rectangle([mx - S(26), my - S(2), mx + S(26), my + S(4)], fill=(255, 255, 255))
    elif m == "frown":
        d.arc([mx - S(28), my - S(2), mx + S(28), my + S(30)], 200, 340, fill=INK, width=S(7))
    elif m == "o":
        d.ellipse([mx - S(14), my - S(16), mx + S(14), my + S(16)], fill=(110, 30, 40), outline=INK, width=S(5))
    elif m == "flat":
        d.line([mx - S(24), my, mx + S(24), my], fill=INK, width=S(7))
    else:  # smirk
        d.arc([mx - S(34), my - S(30), mx + S(30), my + S(10)], 30, 120, fill=INK, width=S(7))
    # lunettes
    sk = pose.get("shades", 0)
    if sk > 0:
        oy = -130 * (1 - ease(sk))
        for k in (-1, 1):
            gx_, gy_ = P(42 * k, -700 + oy)
            d.rounded_rectangle([gx_ - S(40), gy_ - S(26), gx_ + S(40), gy_ + S(26)], S(16), fill=(18, 14, 26), outline=ACC, width=S(5))
            d.line([gx_ - S(24), gy_ - S(10), gx_ - S(6), gy_ - S(20)], fill=(150, 200, 255), width=S(6))
        d.line([P(-4, -706 + oy), P(4, -706 + oy)], fill=ACC, width=S(6))
    # ---- bras (IK) dessines devant
    for k, key in ((-1, "lh"), (1, "rh")):
        sx_, sy_ = 112 * k, -540
        tx_, ty_ = pose.get(key, (165 * k, -300))
        sols = [ik(sx_, sy_, tx_, ty_, 150, 150, b) for b in (-1, 1)]
        score = lambda r: k * r[0] + 0.35 * r[1]  # coude vers l'exterieur et vers le bas
        sols.sort(key=score, reverse=not pose.get("elbow_in"))
        ex_, ey_, hx_, hy_ = sols[0]
        A, B, C = P(sx_, sy_), P(ex_, ey_), P(hx_, hy_)
        for w_, col in ((S(68), INK), (S(54), st["sleeve"])):
            d.line([A, B], fill=col, width=w_); d.line([B, C], fill=col, width=w_)
            d.ellipse([B[0] - w_ / 2, B[1] - w_ / 2, B[0] + w_ / 2, B[1] + w_ / 2], fill=col)
        if st.get("puffer"):
            for w_, col in ((S(84), INK), (S(70), st["sleeve"])):
                d.line([A, B], fill=col, width=w_); d.line([B, C], fill=col, width=w_)
                d.ellipse([B[0] - w_ / 2, B[1] - w_ / 2, B[0] + w_ / 2, B[1] + w_ / 2], fill=col)
            for (P1, P2) in ((A, B), (B, C)):
                vx, vy = P2[0] - P1[0], P2[1] - P1[1]
                nn = math.hypot(vx, vy) or 1
                for f in (0.33, 0.66):
                    mx_, my_ = P1[0] + vx * f, P1[1] + vy * f
                    d.line([mx_ - vy / nn * S(36), my_ + vx / nn * S(36), mx_ + vy / nn * S(36), my_ - vx / nn * S(36)], fill=INK, width=S(5))
                d.line([P1[0] + vx * 0.1 - vy / nn * S(18), P1[1] + vy * 0.1 + vx / nn * S(18), P1[0] + vx * 0.28 - vy / nn * S(18), P1[1] + vy * 0.28 + vx / nn * S(18)], fill=st.get("gloss", (95, 100, 120)), width=S(7))
        d.ellipse([A[0] - S(34), A[1] - S(34), A[0] + S(34), A[1] + S(34)], fill=st["sleeve"], outline=INK, width=lw)
        # manchette
        ux, uy = C[0] - B[0], C[1] - B[1]
        n = math.hypot(ux, uy) or 1
        cx_, cy_ = C[0] - ux / n * S(30), C[1] - uy / n * S(30)
        d.line([cx_ - uy / n * S(30), cy_ + ux / n * S(30), cx_ + uy / n * S(30), cy_ - ux / n * S(30)], fill=st["cuff"], width=S(18))
        if pose.get("watch") and k == -1:
            d.ellipse([cx_ - S(22), cy_ - S(22), cx_ + S(22), cy_ + S(22)], fill=ACC, outline=INK, width=S(5))
            d.line([cx_, cy_, cx_ + S(12) * math.cos(t * 9), cy_ + S(12) * math.sin(t * 9)], fill=INK, width=S(4))
        hand = pose.get(key + "_shape", "fist")
        r = S(30)
        d.ellipse([C[0] - r, C[1] - r, C[0] + r, C[1] + r], fill=st["skin"], outline=INK, width=S(6))
        if hand == "point":
            d.rounded_rectangle([C[0] - S(9), C[1] - S(70), C[0] + S(9), C[1] - S(16)], S(9), fill=st["skin"], outline=INK, width=S(5))
        elif hand == "open":
            for f in (-2, -1, 0, 1):
                fx_ = C[0] + f * S(14) + S(7)
                d.rounded_rectangle([fx_ - S(7), C[1] - S(56), fx_ + S(7), C[1] - S(16)], S(7), fill=st["skin"], outline=INK, width=S(4))
        prop = pose.get(key + "_prop")
        if prop:
            prop(frame, C, s, t)
            d = ImageDraw.Draw(frame)


def draw_puffer_torso(d, P, S, st, lw):
    """Doudoune matelassee : boudins horizontaux brillants, col montant, zip."""
    j, jd, hi = st["jacket"], st["jacket_d"], st.get("gloss", (95, 100, 120))
    rows = [(-585, -520, 138), (-525, -460, 146), (-465, -400, 150), (-405, -340, 148), (-345, -285, 142)]
    for (ya, yb, wdt) in rows:
        d.rounded_rectangle([*P(-wdt, ya), *P(wdt, yb)], S(34), fill=j, outline=INK, width=lw)
        d.rounded_rectangle([*P(wdt - 46, ya + 8), *P(wdt - 8, yb - 8)], S(18), fill=jd)
        d.line([P(-wdt + 34, ya + 16), P(-wdt + 110, ya + 13)], fill=hi, width=S(8))   # reflet brillant
        d.line([P(10, ya + 15), P(46, ya + 14)], fill=hi, width=S(6))
    d.rounded_rectangle([*P(-128, -298), *P(128, -248)], S(18), fill=jd, outline=INK, width=S(5))  # bas elastique
    # col montant
    d.rounded_rectangle([*P(-78, -640), *P(78, -560)], S(30), fill=j, outline=INK, width=lw)
    d.line([P(-50, -625), P(-10, -628)], fill=hi, width=S(6))
    d.line([P(0, -640), P(0, -252)], fill=INK, width=S(6))                         # zip
    d.rounded_rectangle([*P(-9, -602), *P(9, -570)], S(4), fill=ACC, outline=INK, width=S(3))
    if st.get("patch"):  # petit logo ambre sur la poitrine
        cx, cy = P(-70, -430)
        d.ellipse([cx - S(18), cy - S(18), cx + S(18), cy + S(18)], fill=INK, outline=ACC, width=S(4))
        d.polygon([(cx, cy - S(11)), (cx + S(9), cy + S(8)), (cx - S(9), cy + S(8))], fill=ACC)


def draw_cap_back(frame, center, s, hc, hair, t):
    """Casquette snapback portee a l'envers : 6 panneaux, ombrage, coutures, visiere a l'arriere,
    ouverture + sangle a pression sur le front. Dessinee en x3 puis reduite (bords lisses)."""
    Q = 3 * s
    pw, ph = 380, 230
    im = Image.new("RGBA", (int(pw * Q), int(ph * Q)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def q(*v):
        return [x * Q for x in v]
    ink = INK + (255,)
    lw = max(2, int(7 * Q))
    hi, mid, lo = shade(hc, 1.18), hc, shade(hc, 0.78)
    # visiere (a l'arriere, on la voit depasser en haut a droite, dessous plus fonce)
    d.polygon(q(225, 70, 362, 30, 372, 58, 248, 112), fill=shade(hc, 0.62) + (255,), outline=ink, width=lw)
    d.polygon(q(232, 74, 360, 36, 364, 46, 236, 86), fill=shade(hc, 0.9) + (255,))
    for k in range(4):  # surpiqures de la visiere
        d.line(q(250 + k * 6, 82 + k * 5, 352 - k * 2, 46 + k * 3), fill=shade(hc, 0.5) + (255,), width=max(1, int(2 * Q)))
    # calotte (peinte dans son propre calque puis decoupee a la forme du dome)
    box = q(50, 22, 330, 300)
    crown = Image.new("RGBA", im.size, mid + (255,))
    cd = ImageDraw.Draw(crown)
    cd.ellipse(q(10, -40, 200, 220), fill=hi + (255,))                     # reflet gauche
    cd.ellipse(q(250, 0, 420, 260), fill=lo + (255,))                      # ombre droite
    for xa in (-115, -60, 0, 60, 115):                                      # coutures des panneaux
        cd.line(q(190, 22, 190 + xa * 1.25, 165), fill=shade(hc, 0.6) + (255,), width=max(1, int(3 * Q)))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).chord(box, 180, 360, fill=255)
    im.paste(crown, (0, 0), m)
    d = ImageDraw.Draw(im)
    d.chord(box, 180, 360, outline=ink, width=lw)
    # bandeau bas
    d.rectangle(q(50, 150, 330, 161), fill=lo + (255,), outline=ink, width=max(1, int(5 * Q)))
    # ouverture snapback : on voit les cheveux
    d.chord(q(135, 92, 245, 210), 180, 360, fill=hair + (255,), outline=ink, width=max(2, int(6 * Q)))
    # sangle a pression
    d.rounded_rectangle(q(128, 132, 252, 150), int(6 * Q), fill=(28, 26, 36, 255), outline=ink, width=max(1, int(3 * Q)))
    for k in range(5):
        cx = 146 + k * 22
        d.ellipse(q(cx - 5, 136, cx + 5, 146), fill=(200, 200, 215, 255))
    # bouton du dessus + petit patch brode sur le cote
    d.ellipse(q(178, 12, 202, 32), fill=hi + (255,), outline=ink, width=max(1, int(4 * Q)))
    d.ellipse(q(70, 100, 108, 138), fill=(250, 240, 220, 255), outline=ink, width=max(1, int(4 * Q)))
    d.polygon(q(92, 104, 80, 122, 90, 122, 84, 136, 99, 114, 89, 114, 96, 104), fill=ACC + (255,))
    d.arc(q(70, 40, 200, 170), 200, 245, fill=(255, 255, 255, 170), width=max(1, int(6 * Q)))  # brillance
    im = im.resize((max(1, int(pw * s)), max(1, int(ph * s))), Image.LANCZOS).rotate(-5, expand=True, resample=Image.BICUBIC)
    frame.alpha_composite(im, (int(center[0] - im.width / 2 + 0 * s), int(center[1] - im.height / 2 + 10 * s)))


VOC = [0.0, 0.0]  # [energie de la voix 0..1, flash d'attaque 0..1] pour l'image en cours


def vocal_features(path, start, dur, fps):
    """Energie de la bande vocale (350-3500 Hz) par image + instants d'attaque des syllabes."""
    import subprocess as sp
    sr = 16000
    pcm = np.frombuffer(sp.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path, "-ac", "1",
                                "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
    hop, win = sr // fps, 1024
    n = int(dur * fps)
    f = np.fft.rfftfreq(win, 1 / sr)
    band = (f > 350) & (f < 3500)
    env = np.zeros(n)
    for i in range(n):
        seg = pcm[i * hop:i * hop + win]
        if len(seg) < win:
            seg = np.pad(seg, (0, win - len(seg)))
        env[i] = np.abs(np.fft.rfft(seg * np.hanning(win)))[band].sum()
    env = np.convolve(env, np.ones(3) / 3, "same")
    env = np.clip(env / (np.percentile(env, 97) + 1e-9), 0, 1)
    lo = np.convolve(env, np.ones(9) / 9, "same")
    nov = np.clip(env - lo, 0, None)
    thr = np.percentile(nov, 80)
    onsets, last = [], -1
    for i in range(1, n - 1):
        if nov[i] > thr and nov[i] >= nov[i - 1] and nov[i] >= nov[i + 1] and i - last >= int(0.12 * fps):
            onsets.append(i / fps); last = i
    flash = np.zeros(n)
    for o in onsets:
        i0 = int(o * fps)
        for k in range(0, 8):
            if i0 + k < n:
                flash[i0 + k] = max(flash[i0 + k], math.exp(-k / 2.2))
    return env, flash, onsets


def default_pose(t, talk, phase=0):
    g = clamp(talk - 0.25) * 1.4
    return dict(lh=(-170, -300 + 8 * math.sin(t * 5 + phase)), rh=(175 + 20 * g, -300 - 210 * g),
                rh_shape="open" if g > 0.3 else "fist", talk=talk, mouth="smirk")


# ====================================================================== accessoires
def bubble(d, x, y, k, w=240, h=130, col=(255, 255, 255), line=(60, 50, 80), face=None):
    if k <= 0.03:
        return
    w, h = w * k, h * k
    d.polygon([(x + w * 0.2, y + h - 4), (x + w * 0.08, y + h + 40 * k), (x + w * 0.4, y + h - 4)], fill=col, outline=INK)
    d.rounded_rectangle([x, y, x + w, y + h], int(40 * k) + 1, fill=col, outline=INK, width=6)
    if face:
        cx, cy, r = x + w / 2, y + h / 2 + 6 * k, 36 * k
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=face["skin"], outline=INK, width=4)
        if face["hat"] in ("cap_back", "cap"):
            d.chord([cx - r - 2, cy - r - 12 * k, cx + r + 2, cy + r * 0.25], 180, 360, fill=face["hat_col"], outline=INK, width=4)
        elif face["hat"] == "beanie":
            d.chord([cx - r - 2, cy - r - 14 * k, cx + r + 2, cy + r * 0.3], 180, 360, fill=face["hat_col"], outline=INK, width=4)
        else:
            for dx in (-0.6, 0, 0.6):
                d.ellipse([cx + dx * r - 14 * k, cy - r - 12 * k, cx + dx * r + 14 * k, cy - r + 16 * k], fill=face["hair"])
        for e in (-1, 1):
            d.ellipse([cx + e * 12 * k - 4 * k, cy - 6 * k, cx + e * 12 * k + 4 * k, cy + 4 * k], fill=INK)
        return
    for i in range(3):
        yy = y + (h / 4) * (i + 1)
        d.line([x + 30 * k, yy, x + w - (30 + 40 * (i % 2)) * k, yy], fill=line, width=max(1, int(12 * k)))


HIDE_SCENE_TEXT = [False]
ACTIVE = [None]


def big_text(frame, x, y, txt, size, k=1.0, ang=0, col=ACC):
    if k <= 0.03 or (HIDE_SCENE_TEXT[0] and txt != "?"):
        return
    f = font(int(size))
    l, t_, r, b = f.getbbox(txt)
    im = Image.new("RGBA", (r - l + 80, b - t_ + 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((40 - l, 40 - t_), txt, font=f, fill=col, stroke_width=9, stroke_fill=INK)
    im = Image.alpha_composite(im.filter(ImageFilter.GaussianBlur(14)), im)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))))
    if ang:
        im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
    frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def paste(frame, im, x, y, ang=0, k=1.0):
    if k <= 0.03:
        return
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))))
    if ang:
        im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
    frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


_bill = None
def bill_img():
    global _bill
    if _bill is None:
        im = Image.new("RGBA", (340, 170), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([6, 6, 334, 164], 16, fill=(160, 120, 200), outline=INK, width=7)
        d.rounded_rectangle([24, 24, 316, 146], 10, outline=(230, 210, 250), width=4)
        d.ellipse([125, 40, 215, 130], fill=ACC, outline=INK, width=5)
        d.text((40, 28), "500", font=font(44), fill=INK)
        d.text((236, 92), "500", font=font(44), fill=INK)
        _bill = im
    return _bill


def prop_phone(frame, C, s, t):
    d = ImageDraw.Draw(frame)
    x, y = C
    d.rounded_rectangle([x - 34 * s, y - 120 * s, x + 30 * s, y + 10 * s], int(12 * s), fill=(20, 18, 30), outline=INK, width=5)
    d.rounded_rectangle([x - 26 * s, y - 108 * s, x + 22 * s, y - 4 * s], int(8 * s), fill=(110, 230, 200))


def prop_popcorn(frame, C, s, t):
    d = ImageDraw.Draw(frame)
    x, y = C
    d.polygon([(x - 70 * s, y - 60 * s), (x + 70 * s, y - 60 * s), (x + 50 * s, y + 90 * s), (x - 50 * s, y + 90 * s)], fill=(250, 250, 250), outline=INK)
    for k in range(-2, 3):
        d.line([x + k * 26 * s, y - 60 * s, x + k * 20 * s, y + 90 * s], fill=(230, 60, 70), width=int(12 * s))
    for k in range(9):
        px = x - 60 * s + k * 15 * s
        d.ellipse([px - 16 * s, y - 92 * s + (k % 2) * 10 * s, px + 16 * s, y - 60 * s + (k % 2) * 10 * s], fill=(255, 240, 190), outline=INK, width=3)


def clock(d, cx, cy, r, a_min):
    d.ellipse([cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22], fill=(255, 122, 61), outline=INK, width=8)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 250, 235), outline=INK, width=6)
    for i in range(12):
        a = i * math.pi / 6
        d.line([cx + (r - 34) * math.cos(a), cy + (r - 34) * math.sin(a), cx + (r - 10) * math.cos(a), cy + (r - 10) * math.sin(a)], fill=INK, width=8)
    d.line([cx, cy, cx + r * 0.5 * math.cos(a_min / 12), cy + r * 0.5 * math.sin(a_min / 12)], fill=INK, width=16)
    d.line([cx, cy, cx + r * 0.82 * math.cos(a_min), cy + r * 0.82 * math.sin(a_min)], fill=(230, 60, 70), width=10)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=ACC, outline=INK, width=4)
    for k in (-1, 1):  # cloches du reveil
        bx = cx + k * r * 0.7
        d.chord([bx - 60, cy - r - 70, bx + 60, cy - r + 40], 180, 360, fill=ACC, outline=INK, width=6)


def mic(d, x0, y0, x1, y1, col):
    d.line([x0, y0, x1, y1], fill=INK, width=30)
    d.line([x0, y0, x1, y1], fill=col, width=18)
    d.ellipse([x1 - 34, y1 - 34, x1 + 34, y1 + 34], fill=(200, 200, 215), outline=INK, width=6)
    for k in (-14, 0, 14):
        d.line([x1 - 24, y1 + k, x1 + 24, y1 + k], fill=(140, 140, 160), width=4)


def burst(d, x, y, k, col=(255, 255, 255)):
    for i in range(8):
        a = i * math.pi / 4
        d.line([x + 30 * k * math.cos(a), y + 30 * k * math.sin(a), x + 70 * k * math.cos(a), y + 70 * k * math.sin(a)], fill=col, width=8)


def rain(frame, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    rnd = random.Random(3)
    for _ in range(170):
        x, y0, v = rnd.random() * W * 1.2, rnd.random() * H, rnd.uniform(1500, 2100)
        y = (y0 + v * t) % (H + 100) - 50
        xx = x - (y / H) * 160
        ld.line([xx, y, xx - 14, y + 50], fill=(200, 210, 255, 130), width=3)
    for i in range(6):  # eclaboussures
        ph = (t * 1.7 + i * 0.37) % 1
        x = 100 + i * 170
        ld.ellipse([x - 40 * ph, 1780 - 10 * ph, x + 40 * ph, 1780 + 10 * ph], outline=(220, 230, 255, int(200 * (1 - ph))), width=3)
    frame.alpha_composite(lay)


# ====================================================================== actions
def A_bored(c):
    """Le heros s'ennuie a cote du groupe, regarde son tel."""
    lt, t = c["lt"], c["t"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(rh=(40, -560), rh_prop=prop_phone, lh=(-60, -420), elbow_in=False, look=(0.6, 1), brows="skeptic",
                 mouth="flat" if talk < 0.2 else "smirk")
        return p
    extras = [dict(x=600 + i * 170, seed=i, pose="chat") for i in range(3)]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(3):
            bubble(d, 520 + i * 150, c["gy"] - 980 - (i % 2) * 80, eob((lt - 0.2 - i * 0.3) / 0.3), 200, 115,
                   col=[(255, 255, 255), (255, 210, 120), (150, 230, 240)][i])
    return dict(hero=hero, hx=280, extras=extras, front=front)


def A_walk_away(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        wave = lt < 0.9
        p.update(walk=1 if lt > 0.3 else 0, lh=(-90, -330),
                 rh=(150 + 30 * math.sin(t * 14), -720) if wave else (90, -330),
                 rh_shape="open" if wave else "fist", look=(-1, 0), brows="neutral")
        return p
    hx = 480 + 760 * ease((lt - 0.3) / 1.6)
    extras = [dict(x=120 + i * 150, seed=i + 3, pose="laugh") for i in range(3)]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(2):
            bubble(d, 20 + i * 220, c["gy"] - 960 - i * 60, eob((lt - 0.4 - i * 0.3) / 0.3), 200, 110)
        big_text(fr, 780, c["gy"] - 1000, "BYE", 110, eob((lt - 0.1) / 0.3) * (1 - ease((lt - 1.2) / 0.3)), ang=-10)
    return dict(hero=hero, hx=hx, extras=extras, front=front)


def press_mics(fr, c, retreat=0.0):
    d = ImageDraw.Draw(fr)
    rnd = random.Random(5)
    cols = [(230, 60, 70), (60, 150, 230), (250, 190, 60), (120, 200, 120), (190, 110, 230), (240, 240, 240)]
    for i in range(6):
        side = -1 if i % 2 else 1
        k = ease((c["lt"] - i * 0.1) / 0.4) * (1 - 0.6 * retreat)
        tx = c["hx"] + side * (190 + rnd.randint(0, 60))
        ty = c["gy"] - 720 + rnd.randint(-120, 200)
        sx = tx + side * 700
        mic(d, sx, ty + 260, sx + (tx - sx) * k, ty + 260 - 260 * k, cols[i])
        if k > 0.9:  # flash d'appareil photo
            if (c["t"] * 3 + i * 0.37) % 1 < 0.08:
                burst(d, tx + side * 120, ty - 120, 1.2)


def A_press(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(rh=(120, -720), rh_shape="open", lh=(-170, -300), brows="angry", look=(0.3, 0), mouth="frown" if talk < 0.2 else "smirk")
        return p
    def front(fr, c):
        big_text(fr, c["hx"] - 230, c["gy"] - 1060 + 12 * math.sin(c["t"] * 5), "?", 280, eob((lt - 0.35) / 0.3), ang=12)
    return dict(hero=hero, hx=540, back=lambda fr, c: press_mics(fr, c), front=front)


def A_shrug(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        up = ease(lt / 0.3)
        p.update(lh=(-250, -560 - 80 * up), rh=(250, -560 - 80 * up), lh_shape="open", rh_shape="open",
                 brows="up", mouth="smirk" if talk < 0.2 else "talk", look=(0, -1), bob=-10 * up)
        return p
    def front(fr, c):
        big_text(fr, c["hx"], c["gy"] - 1080, "BAH...", 120, eob((lt - 0.3) / 0.3), ang=-6, col=(255, 255, 255))
    return dict(hero=hero, hx=540, back=lambda fr, c: press_mics(fr, c, retreat=ease(lt / 0.8)), front=front)


def A_whisper(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(70, -430), rh=(-70, -415), elbow_in=False, brows="angry", look=(1, 0), mouth="flat" if talk < 0.25 else "smirk")
        return p
    extras = [dict(x=600 + i * 160, seed=i + 7, pose="whisper" if i % 2 == 0 else "listen", look=(-1, 0)) for i in range(3)]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(3):
            bubble(d, 480 + i * 170, c["gy"] - 1000 - (i % 2) * 90, eob((lt - 0.15 - i * 0.3) / 0.3), 170, 120, face=ACTIVE[0])
    return dict(hero=hero, hx=230, extras=extras, front=front)


def A_friend_with(c):
    """Ton ami avec eux : ca rigole, et on parle du heros (bulles avec sa tete)."""
    lt = c["lt"]
    extras = [dict(x=300, style=FRIEND, pose="laugh"),
              dict(x=520, seed=11, pose="whisper"), dict(x=730, seed=12, pose="laugh"), dict(x=930, seed=13, pose="listen")]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(2):
            bubble(d, 420 + i * 260, c["gy"] - 1020 - i * 70, eob((lt - 0.3 - i * 0.3) / 0.3), 180, 125, face=ACTIVE[0])
    return dict(hero=None, extras=extras, front=front)


def A_me_with(c):
    """Le heros avec eux : sourires forces, et on parle de l'ami (bulles avec sa tete)."""
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(brows="skeptic", look=(1, 0), mouth="flat" if talk < 0.25 else "smirk", lh=(-100, -330), rh=(100, -330))
        return p
    extras = [dict(x=560 + i * 170, seed=14 + i, pose="whisper" if i == 1 else "laugh", look=(-1, 0)) for i in range(3)]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(2):
            bubble(d, 520 + i * 220, c["gy"] - 1020 - i * 70, eob((lt - 0.2 - i * 0.3) / 0.3), 180, 125, face=FRIEND)
    return dict(hero=hero, hx=280, extras=extras, front=front)


def A_envious(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        put = ease((lt - 0.5) / 0.4)
        p.update(rh=(60 + 0 * put, -720 + 140 * (1 - put) if put < 1 else -330), rh_shape="fist" if put < 1 else "fist",
                 shades=put, brows="neutral", mouth="smirk" if talk < 0.25 else "talk", look=(-1, 0))
        if put >= 1:
            p.update(rh=(175, -300))
        return p
    def overlay(fr, c):
        lay = Image.new("RGBA", (W, H), (10, 6, 30, int(170 * ease(lt / 0.4))))
        ld = ImageDraw.Draw(lay)
        rnd = random.Random(9)
        cols = [(255, 200, 60), (120, 255, 140), (255, 90, 160)]
        for i in range(12):
            x, y = rnd.randint(80, W - 80), rnd.randint(520, 1600)
            if abs(x - c["hx"]) < 200 and y > c["gy"] - 900:
                continue
            k = ease((lt - 0.1 - i * 0.07) / 0.2)
            bl = (c["t"] * 0.9 + i * 0.37) % 2.2 < 0.12
            h = 0 if bl else 32 * k
            look = 12 if x < c["hx"] else -12
            col = cols[i % 3]
            for sx in (-42, 42):
                ld.ellipse([x + sx - 32, y - h, x + sx + 32, y + h], fill=col + (255,))
                if not bl and k > 0.5:
                    ld.ellipse([x + sx + look * 1.5 - 12, y - 14, x + sx + look * 1.5 + 12, y + 14], fill=INK + (255,))
            ld.line([x - 74, y - 40, x - 14, y - 26], fill=col + (255,), width=8)
            ld.line([x + 74, y - 40, x + 14, y - 26], fill=col + (255,), width=8)
        fr.alpha_composite(lay)
    def front(fr, c):
        if lt > 0.95:
            big_text(fr, c["hx"] + 210, c["gy"] - 980, "COOL", 100, eob((lt - 0.95) / 0.3), ang=10, col=(120, 230, 255))
    return dict(hero=hero, hx=540, pre_hero=overlay, front=front)


def A_rumors(c, cover=False):
    lt = c["lt"]
    rnd = random.Random(11 + cover)
    pos = [(rnd.randint(20, W - 280), rnd.randint(480, 1350), rnd.uniform(0.6, 1.1)) for _ in range(12)]
    def hero(t, talk):
        p = default_pose(t, talk)
        if cover:
            p.update(lh=(-120, -720), rh=(120, -720), lh_shape="open", rh_shape="open", eyes="closed", brows="angry", mouth="frown")
        else:
            sw = math.sin(t * 9)
            p.update(rh=(160 + 120 * sw, -760), rh_shape="open", brows="angry", look=(sw, -1))
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        cols = [(255, 255, 255), (255, 210, 120), (150, 230, 240), (255, 160, 200)]
        for i, (x, y, sc) in enumerate(pos):
            k = eob((lt - i * 0.1) / 0.25)
            near = abs(x + 120 - c["hx"]) < 260 and abs(y - (c["gy"] - 800)) < 260
            if not cover and near and lt > 0.6 + i * 0.05:  # le heros eclate la bulle
                pk = clamp((lt - 0.6 - i * 0.05) / 0.2)
                if pk < 1:
                    burst(d, x + 120, y + 60, 0.6 + pk, ACC)
                continue
            bubble(d, x, y + 8 * math.sin(c["t"] * 4 + i), k * sc, 240, 130, col=cols[i % 4])
        big_text(fr, 300, 600, "BLA BLA", 110, eob((lt - 0.5) / 0.3), ang=-8, col=(255, 255, 255))
    return dict(hero=hero, hx=540 if not cover else 540, extras=[dict(x=x_, seed=20 + i, pose="chat") for i, x_ in enumerate((90, 990))], front=front)


def A_target(c):
    lt = c["lt"]
    throw = 0.45
    def hero(t, talk):
        p = default_pose(t, talk)
        if lt < throw:
            p.update(rh=(230, -760), look=(1, 0), brows="angry")
        elif lt < throw + 0.25:
            p.update(rh=(290, -560), rh_shape="open", look=(1, 0))
        else:  # facepalm
            k = ease((lt - throw - 0.6) / 0.3)
            p.update(rh=(290 - 260 * k, -560 - 150 * k), rh_shape="open", look=(1, 0), brows="sad", mouth="frown")
        return p
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        cx, cy = 820, c["gy"] - 780
        for i, col in enumerate([(250, 250, 240), (230, 60, 70), (250, 250, 240), (230, 60, 70), ACC]):
            r = 170 - i * 34
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=INK, width=5)
        d.line([cx, cy + 170, cx - 60, c["gy"] - 300], fill=(120, 80, 50), width=14)
        d.line([cx, cy + 170, cx + 60, c["gy"] - 300], fill=(120, 80, 50), width=14)
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = ease((lt - throw) / 0.35)
        if lt < throw:
            x, y = c["hx"] + 230 * 1, c["gy"] - 840
        else:
            x0, y0 = c["hx"] + 280, c["gy"] - 640
            x1, y1 = 1010, c["gy"] - 1000
            x, y = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k - 200 * math.sin(math.pi * k)
        d.line([x - 110, y + 16, x, y], fill=INK, width=16)
        d.polygon([(x - 110, y + 16), (x - 160, y - 20), (x - 150, y + 52)], fill=(60, 200, 220), outline=INK)
        if k >= 1:
            big_text(fr, 900, c["gy"] - 1130, "RATÉ", 90, eob((lt - throw - 0.35) / 0.3), ang=12, col=(255, 90, 110))
    return dict(hero=hero, hx=300, back=back, front=front)


def A_drama(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        eat = (t * 1.2) % 1 < 0.4
        p.update(lh=(-130, -330), lh_prop=prop_popcorn, rh=(-20, -630) if eat else (-80, -420),
                 eyes="sleepy", brows="neutral", mouth="o" if eat else "flat", look=(1, -1))
        return p
    extras = [dict(x=330 + i * 160, seed=30 + i, pose="drama", s=0.62, gy_off=-150) for i in range(4)]
    def back(fr, c):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(500, 440), (640, 440), (980, c["gy"] - 140), (260, c["gy"] - 140)], fill=(255, 220, 120, 70))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(10):  # tetes du public de dos
            hx_ = 60 + i * 120
            if 120 < hx_ < 400:
                continue
            d.ellipse([hx_ - 55, 1700, hx_ + 55, 1820], fill=(50, 16, 32), outline=INK, width=5)
            d.rounded_rectangle([hx_ - 80, 1790, hx_ + 80, H + 40], 50, fill=(50, 16, 32))
        big_text(fr, 760, 700, "!!!", 140, eob((lt - 0.2) / 0.3), ang=10, col=(255, 90, 110))
    return dict(hero=hero, hx=240, hero_s=1.05, hero_gy=1960, extras=extras, back=back, front=front)


def A_time(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(-40, -500), elbow_in=False, watch=True, look=(-0.6, 1), brows="up", mouth="o" if talk < 0.25 else "talk")
        return p
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        clock(d, 660, 830, 210, c["t"] * 8)
        rnd = random.Random(13)
        for i in range(12):
            ph = (lt * 0.9 + i * 0.083) % 1
            x = rnd.randint(-100, W) + 400 * ph
            y = 1600 - 1300 * ph + 40 * math.sin(c["t"] * 3 + i)
            im = Image.new("RGBA", (110, 124), (0, 0, 0, 0))
            dd = ImageDraw.Draw(im)
            dd.rectangle([4, 4, 106, 120], fill=(255, 252, 240), outline=INK, width=5)
            dd.rectangle([4, 4, 106, 36], fill=(230, 60, 70), outline=INK, width=5)
            dd.text((55, 80), str(rnd.randint(1, 31)), font=font(50), fill=INK, anchor="mm")
            paste(fr, im, x, y, ang=(c["t"] * 140 + i * 40) % 360)
    return dict(hero=hero, hx=270, back=back)


def A_hourglass(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(70, -430), rh=(-70, -415), brows="angry", look=(1, 0.3), mouth="flat" if talk < 0.25 else "talk",
                 tap=max(0, math.sin(t * 14)) * 20)
        return p
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        cx, cy, hw, hh = 760, c["gy"] - 640, 150, 250
        f = clamp(lt / max(0.5, c["dur"]))
        wood = (150, 92, 52)
        d.rounded_rectangle([cx - hw - 40, cy - hh - 46, cx + hw + 40, cy - hh], 12, fill=wood, outline=INK, width=6)
        d.rounded_rectangle([cx - hw - 40, cy + hh, cx + hw + 40, cy + hh + 46], 12, fill=wood, outline=INK, width=6)
        for sx in (-hw - 26, hw + 14):
            d.rectangle([cx + sx, cy - hh, cx + sx + 12, cy + hh], fill=wood, outline=INK, width=4)
        d.polygon([(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + 16, cy), (cx + hw, cy + hh), (cx - hw, cy + hh), (cx - 16, cy)], fill=(200, 240, 250))
        top = (1 - f) * 0.9
        d.polygon([(cx - hw * top, cy - hh * top), (cx + hw * top, cy - hh * top), (cx, cy)], fill=ACC)
        bot = f * 0.9
        d.polygon([(cx - hw, cy + hh), (cx + hw, cy + hh), (cx + hw * (1 - bot), cy + hh * (1 - bot)), (cx - hw * (1 - bot), cy + hh * (1 - bot))], fill=ACC)
        d.line([cx, cy, cx, cy + hh], fill=ACC, width=6)
        d.line([(cx - hw, cy - hh), (cx - 16, cy), (cx - hw, cy + hh)], fill=INK, width=7)
        d.line([(cx + hw, cy - hh), (cx + 16, cy), (cx + hw, cy + hh)], fill=INK, width=7)
        d.line([cx - hw + 30, cy - hh + 20, cx - 40, cy - 60], fill=(255, 255, 255), width=8)
    return dict(hero=hero, hx=290, back=back)


def A_idea(c):
    lt = c["lt"]
    pop = 0.55
    def hero(t, talk):
        p = default_pose(t, talk)
        if lt < pop:
            p.update(rh=(60, -600), look=(1, -1), brows="skeptic", mouth="flat")
        else:
            p.update(rh=(150, -840), rh_shape="point", look=(0.3, -1), brows="up", mouth="smile" if talk < 0.25 else "talk")
        return p
    def front(fr, c):
        k = eob((lt - pop) / 0.3)
        if k < 0.03:
            return
        x, y = c["hx"] + 10, c["gy"] - 1110
        glow(fr, x, y, 160 * k * (1 + 0.1 * c["p"]), ACC, 150)
        d = ImageDraw.Draw(fr)
        r = 90 * k
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 230, 120), outline=INK, width=7)
        d.arc([x - r * 0.5, y - r * 0.5, x + r * 0.3, y + r * 0.3], 180, 270, fill=(255, 255, 255), width=10)
        d.rectangle([x - 40 * k, y + r - 10, x + 40 * k, y + r + 50 * k], fill=(150, 150, 170), outline=INK, width=6)
        for i in range(8):
            a = i * math.pi / 4 + c["t"]
            d.line([x + (r + 25) * math.cos(a), y + (r + 25) * math.sin(a), x + (r + 60 * k) * math.cos(a), y + (r + 60 * k) * math.sin(a)], fill=ACC, width=9)
    return dict(hero=hero, hx=420, front=front)


def A_phone(c):
    lt = c["lt"]
    pick = 0.6
    def hero(t, talk):
        p = default_pose(t, talk)
        if lt < pick:
            p.update(look=(1, 0.5), brows="up", mouth="o")
        else:
            p.update(rh=(140, -700), rh_prop=prop_phone, brows="neutral", mouth="smile" if talk < 0.25 else "talk", look=(1, 0))
        return p
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        tx0, ty = 520, c["gy"] - 330
        d.rounded_rectangle([tx0, ty, tx0 + 480, ty + 40], 10, fill=(201, 138, 84), outline=INK, width=6)
        for lx in (tx0 + 30, tx0 + 450):
            d.rectangle([lx - 10, ty + 40, lx + 10, c["gy"] + 10], fill=(150, 96, 56), outline=INK, width=4)
        if lt < pick:  # le telephone vibre sur la table
            sh = 8 * math.sin(c["t"] * 70)
            px, py = 760 + sh, ty - 10
            d.rounded_rectangle([px - 90, py - 30, px + 90, py + 10], 12, fill=(20, 18, 30), outline=INK, width=5)
            d.rounded_rectangle([px - 78, py - 24, px + 78, py + 4], 8, fill=(110, 230, 200))
            for i in range(3):
                d.arc([px - 120 - i * 30, py - 80 - i * 20, px + 120 + i * 30, py + 40 + i * 20], 200, 340, fill=ACC, width=7)
    def front(fr, c):
        if lt > pick:
            b = bill_img()
            rnd = random.Random(17)
            for i in range(5):  # billets qui s'envolent du telephone
                ph = clamp((lt - pick - i * 0.15) / 1.2)
                if ph <= 0:
                    continue
                x = c["hx"] + 160 + 300 * ph + rnd.randint(-40, 40)
                y = c["gy"] - 760 - 500 * ph
                paste(fr, b, x, y, ang=40 * math.sin(c["t"] * 4 + i), k=0.45)
            big_text(fr, 790, c["gy"] - 1150, "ALLÔ ?", 100, eob((lt - pick) / 0.3), ang=-8, col=(120, 230, 200))
    return dict(hero=hero, hx=330, back=back, front=front)


def A_broken(c):
    lt = c["lt"]
    brk = 0.9
    def hero(t, talk):
        p = default_pose(t, talk)
        if lt < brk:
            p.update(rh=(250, -420), rh_shape="fist", look=(1, 0), mouth="smile")
        else:
            p.update(rh=(220, -420), rh_shape="open", look=(1, 0.3), brows="sad", mouth="frown")
        return p
    fx = 760 + 200 * ease((lt - brk - 0.2) / 0.6)
    def friend_pose(t, talk):
        p = default_pose(t, talk, 1)
        if lt < brk:
            p.update(lh=(-230, -420), look=(-1, 0), mouth="smile")
        else:
            p.update(lh=(-90, -720), lh_shape="open", rh=(90, -720), rh_shape="open", look=(-1, -1), brows="up", mouth="smile",
                     walk=1 if lt > brk + 0.2 else 0)
        return p
    extras = [dict(x=fx, style=FRIEND, posefn=friend_pose)]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        b = bill_img()
        for i in range(2):
            k = ease((lt - i * 0.2) / 0.7)
            if lt < brk:
                paste(fr, b, 560 + i * 120, -200 + (c["gy"] - 1000 + 200) * k, ang=(1 - k) * 200 + i * 20, k=0.6)
            else:
                paste(fr, b, fx - 20 + i * 40, c["gy"] - 860 - i * 30, ang=-10 + i * 20, k=0.5)
        if lt > brk:  # cassure : un coeur qui se fend
            k = eob((lt - brk) / 0.3)
            x, y = 560, c["gy"] - 1100
            for side in (-1, 1):
                off = side * 26 * ease((lt - brk) / 0.4)
                d.pieslice([x - 80 * k + off, y - 60 * k, x + 80 * k + off, y + 100 * k], 90 if side == -1 else -90, 270 if side == -1 else 90, fill=(230, 60, 90), outline=INK, width=6)
            d.line([(x, y - 40 * k), (x - 20 * k, y), (x + 15 * k, y + 30 * k), (x, y + 80 * k)], fill=INK, width=10)
    return dict(hero=hero, hx=300, extras=extras, front=front)


def A_slice(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        k = ease((lt - 0.8) / 0.3)
        p.update(lh=(-170 - 80 * k, -330 - 240 * k), rh=(170 + 80 * k, -330 - 240 * k), lh_shape="open", rh_shape="open",
                 brows="angry" if k > 0.5 else "neutral", look=(1, 0.5), mouth="o" if k > 0.5 and talk < 0.25 else "smirk")
        return p
    def friend_pose(t, talk):
        p = default_pose(t, talk, 2)
        take = ease((lt - 0.3) / 0.8)
        p.update(lh=(-260 + 120 * take, -470), lh_shape="open", look=(-1, 0.6), mouth="smile", brows="up")
        return p
    extras = [dict(x=800, style=FRIEND, posefn=friend_pose)]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        ty = c["gy"] - 380
        d.rounded_rectangle([140, ty, 940, ty + 46], 12, fill=(201, 138, 84), outline=INK, width=6)
        for lx in (180, 900):
            d.rectangle([lx - 12, ty + 46, lx + 12, c["gy"] + 20], fill=(150, 96, 56), outline=INK, width=4)
        cx, cy = 540, ty - 20
        d.ellipse([cx - 220, cy - 40, cx + 220, cy + 40], fill=(245, 245, 250), outline=INK, width=6)
        take = ease((lt - 0.3) / 0.8)
        # petite part qui reste au heros
        d.pieslice([cx - 170, cy - 140, cx + 170, cy + 40], 200, 250, fill=(255, 240, 220), outline=INK, width=6)
        d.pieslice([cx - 170, cy - 150, cx + 170, cy + 30], 200, 250, fill=(240, 120, 150), outline=INK, width=6)
        # grosse part qui glisse vers l'ami
        ox = 260 * take
        d.pieslice([cx - 170 + ox, cy - 140, cx + 170 + ox, cy + 40], 250, 560, fill=(255, 240, 220), outline=INK, width=6)
        d.pieslice([cx - 170 + ox, cy - 150, cx + 170 + ox, cy + 30], 250, 560, fill=(240, 120, 150), outline=INK, width=6)
        for a in (290, 340, 30, 80, 130):
            r = math.radians(a)
            x, y = cx + ox + 110 * math.cos(r), cy - 60 + 50 * math.sin(r)
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(230, 40, 60), outline=INK, width=4)
        if lt > 1.1:
            big_text(fr, 300, c["gy"] - 1150, "HEIN ?!", 110, eob((lt - 1.1) / 0.3), ang=-8, col=(255, 90, 110))
    return dict(hero=hero, hx=280, extras=extras, front=front)


def A_alone(c):
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(-90, -330), rh=(90, -330), hood=True, look=(0, 1), brows="sad", mouth="flat" if talk < 0.25 else "talk", walk=0.5)
        return p
    def overlay(fr, c):
        fr.alpha_composite(Image.new("RGBA", (W, H), (10, 10, 40, 120)))
    return dict(hero=hero, hx=540 + 40 * c["lt"], pre_hero=overlay, front=lambda fr, c: rain(fr, c["t"]))


def A_empty(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(-280, -520), rh=(280, -520), lh_shape="open", rh_shape="open", look=(math.sin(t * 2.2), 0),
                 brows="up", mouth="o" if talk < 0.25 else "talk")
        return p
    def back(fr, c):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(480, 440), (600, 440), (900, c["gy"]), (180, c["gy"])], fill=(255, 220, 120, 80))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for row in range(2):  # fauteuils vides
            y = 1700 + row * 140
            for i in range(7):
                x = 80 + i * 155 + row * 40
                d.rounded_rectangle([x - 62, y - 90, x + 62, y + 20], 20, fill=(180, 40, 60), outline=INK, width=6)
                d.rounded_rectangle([x - 70, y + 10, x + 70, y + 50], 14, fill=(150, 30, 50), outline=INK, width=6)
        big_text(fr, c["hx"] + 240 * math.sin(c["t"] * 2), c["gy"] - 1080, "?", 180, eob((lt - 0.3) / 0.3))
    return dict(hero=hero, hx=540, back=back, front=front)


ACTIONS = dict(bored=A_bored, walk_away=A_walk_away, press=A_press, shrug=A_shrug, whisper=A_whisper,
               friend_with=A_friend_with, me_with=A_me_with, envious=A_envious, rumors=A_rumors,
               rumors_cover=lambda c: A_rumors(c, cover=True), target=A_target, drama=A_drama, time=A_time,
               hourglass=A_hourglass, idea=A_idea, phone=A_phone, broken=A_broken, slice=A_slice, alone=A_alone,
               empty=A_empty)


def extra_pose(kind, t, talk, phase, look):
    p = default_pose(t, 0.0, phase)
    p["talk"] = 0
    if kind == "chat":
        g = max(0, math.sin(t * 5 + phase * 2))
        p.update(rh=(170, -320 - 200 * g), rh_shape="open", talk=0.3 * g, mouth="smile")
    elif kind == "laugh":
        p.update(lh=(-120, -380), rh=(120, -380), mouth="smile", eyes="closed" if math.sin(t * 8 + phase) > 0 else None, bob=6 * math.sin(t * 16 + phase))
    elif kind == "whisper":
        p.update(rh=(-20, -620), rh_shape="open", look=look, mouth="o", brows="up")
    elif kind == "listen":
        p.update(look=look, mouth="o", brows="up")
    elif kind == "drama":
        a = t * 6 + phase
        p.update(lh=(-260 + 40 * math.sin(a), -720 + 80 * math.cos(a)), rh=(260 + 40 * math.cos(a), -700 + 80 * math.sin(a)),
                 lh_shape="open", rh_shape="open", mouth="o", brows="sad", eyes="closed")
    if look and "look" not in p:
        p["look"] = look
    p.setdefault("look", look or (0, 0))
    return p


# ====================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyrics", required=True)
    ap.add_argument("--audio")
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--duration", type=float, default=60)
    ap.add_argument("--bpm", type=float, default=95)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", default="video_cartoon2.mp4")
    ap.add_argument("--stills", help="liste de temps -> planche PNG")
    ap.add_argument("--hero", default="classic", choices=["classic", "dark"])
    ap.add_argument("--night", action="store_true", help="etalonnage nocturne des decors")
    a = ap.parse_args()
    fps, dur = a.fps, a.duration
    ACTIVE[0] = HERO_DARK if a.hero == "dark" else HERO

    lines = load_lyrics(a.lyrics, a.start)
    raw = json.load(open(a.lyrics, encoding="utf-8"))
    for i, l in enumerate(lines):
        l["scene"] = raw[i].get("scene", "street")
        l["action"] = raw[i].get("action")
        l["seed"] = i
    rms, pulse = audio_energy(a.audio, a.start, dur, fps) if a.audio else bpm_energy(a.bpm, dur, fps)
    talk_env = np.convolve(rms, np.ones(3) / 3, "same")
    venv, vflash, onsets = (vocal_features(a.audio, a.start, dur, fps) if a.audio else (np.zeros(int(dur * fps)), np.zeros(int(dur * fps)), []))
    talk_env = 0.4 * talk_env + 0.6 * venv
    venv = np.convolve(venv, np.ones(9) / 9, "same")  # lumieres sans a-coups
    vflash = vflash * 0
    for l in lines:  # chaque mot du sous-titre apparait sur une attaque de la voix
        ws = [w for w in l["words"] if w["text"]]
        on = [o for o in onsets if l["start"] - 0.05 <= o < l["end"] - 0.25]
        if ws and len(on) >= len(ws):
            idx = np.linspace(0, len(on) - 1, len(ws)).round().astype(int)
            for w, j in zip(ws, idx):
                w["t"] = on[j]

    cache, lights = {}, {}
    def bg_for(scene):
        if scene not in cache:
            img = SCENES[scene][0](random.Random(42)).convert("RGBA")
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            tint = TOP_TINT[scene]
            for y in range(0, 620):
                a_ = 1.0 if y < 360 else max(0, 1 - (y - 360) / 260) ** 1.3
                od.line([0, y, W, y], fill=tint + (int(250 * a_),))
            img = Image.alpha_composite(img, ov)
            if a.night:  # nuit : on assombrit et on bleuit, mais les lumieres (neons, fenetres) restent vives
                f = np.asarray(img.convert("RGB")).astype(np.float32)
                lum = f.mean(2, keepdims=True) / 255
                keep = np.clip((lum - 0.62) / 0.3, 0, 1) * (f.max(2, keepdims=True) - f.min(2, keepdims=True) > 60)
                night = f * np.array([0.42, 0.42, 0.62]) + np.array([6, 4, 22])
                f = night * (1 - keep) + f * keep
                yy = np.linspace(-1, 1, H)[:, None, None]; xx = np.linspace(-1, 1, W)[None, :, None]
                f *= 1 - 0.35 * np.clip((xx ** 2 + yy ** 2) - 0.3, 0, 1)
                img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).convert("RGBA")
            arr = np.asarray(img.convert("RGB")).astype(np.int16)
            arr += np.random.default_rng(len(cache)).integers(-6, 7, (H, W, 1))
            cache[scene] = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
            # calque des lumieres du decor (neons, fenetres, lampes) qui va pulser avec la voix
            f = np.asarray(cache[scene].convert("RGB")).astype(np.float32)
            lum = f.mean(2, keepdims=True) / 255
            sat = (f.max(2, keepdims=True) - f.min(2, keepdims=True)) > 50
            m = np.clip((lum - 0.5) / 0.3, 0, 1) * sat
            gl = Image.fromarray(np.clip(f * m, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
            lights[scene] = (np.asarray(cache[scene].convert("RGB")).astype(np.float32), np.asarray(gl).astype(np.float32))
        return cache[scene]

    dust = [(random.random() * W, random.random() * H, random.uniform(2, 5), random.uniform(10, 35)) for _ in range(40)]

    def render(fi):
        t = fi / fps
        cur = [i for i, l in enumerate(lines) if l["start"] - 0.25 <= t]
        li = cur[-1] if cur else 0
        line = lines[li]
        scene = line["scene"]
        gy = SCENES[scene][1]
        bg_for(scene)
        fi_ = min(fi, len(venv) - 1)
        VOC[0], VOC[1] = float(venv[fi_]), float(vflash[fi_])
        base, gl = lights[scene]
        inten = 0.25 + 0.75 * VOC[0]
        frame = Image.fromarray(np.clip(base + gl * inten, 0, 255).astype(np.uint8)).convert("RGBA")
        lt = t - (line["start"] - 0.25)
        p = float(pulse[min(fi, len(pulse) - 1)])
        singing = any(l["start"] <= t < l["end"] for l in lines)
        talk = float(talk_env[min(fi, len(talk_env) - 1)]) if singing else 0.05
        c = dict(t=t, lt=lt, dur=line["end"] - line["start"] + 0.25, gy=gy, p=p, hx=540)
        HIDE_SCENE_TEXT[0] = any(w["text"] for w in line["words"])
        cfg = ACTIONS[line["action"] or "bored"](c)
        hx = cfg.get("hx", 540)
        c["hx"] = hx
        if cfg.get("back"):
            cfg["back"](frame, c)
        for k, e in enumerate(cfg.get("extras", [])):
            st = e.get("style") or random_style(random.Random(100 + e.get("seed", k)))
            look = e.get("look") or ((-1, 0) if (cfg.get("hero") and hx < e["x"]) else (1, 0))
            if e.get("posefn"):
                pose = e["posefn"](t, 0)
            else:
                pose = extra_pose(e.get("pose", "chat"), t, 0, k * 1.7, look)
            draw_person(frame, e["x"], gy + e.get("gy_off", 0) - 6 * k, t, st, pose, s=e.get("s", 0.8), phase=k * 1.7)
        if cfg.get("pre_hero"):
            cfg["pre_hero"](frame, c)
        if cfg.get("hero"):
            pose = cfg["hero"](t, talk)
            pose.setdefault("talk", talk)
            if pose.get("mouth") in ("smile", "frown", "flat", "o") and talk > 0.3:
                pass
            draw_person(frame, hx, cfg.get("hero_gy", gy), t, ACTIVE[0], pose, s=0.92 * cfg.get("hero_s", 1.0))
        if cfg.get("front"):
            cfg["front"](frame, c)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for (x, y, r, v) in dust:
            yy = (y - v * t) % H
            ld.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 255, 255, 60))
        frame.alpha_composite(lay)
        z = 1.0 + 0.035 * min(1, lt / 4)  # zoom lent uniquement : plus de secousse ni de coup de zoom
        cw, ch = int(W / z), int(H / z)
        ox = (W - cw) // 2
        oy = int((H - ch) * 0.6)
        frame = frame.crop((ox, oy, ox + cw, oy + ch)).resize((W, H), Image.BILINEAR)
        for l in lines:
            if l["start"] - 0.25 <= t < l["end"] and any(w["text"] for w in l["words"]):
                draw_lyrics(frame, l, t, p)
                break
        return frame.convert("RGB")

    if a.stills:
        ts = [float(x) for x in a.stills.split(",")]
        ims = [render(int(x * fps)).resize((270, 480)) for x in ts]
        cols = min(10, len(ims))
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (270 * cols, 480 * rows))
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
        sheet.save(a.out)
        print("OK ->", a.out)
        return

    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if a.audio:
        cmd += ["-ss", str(a.start), "-t", str(dur), "-i", a.audio, "-c:a", "aac", "-b:a", "192k", "-af", f"afade=t=out:st={dur - 1.2}:d=1.2"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-shortest", a.out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(dur * fps)):
        enc.stdin.write(render(fi).tobytes())
        if fi % (fps * 10) == 0:
            print(f"{fi / fps:5.1f}s / {dur:.0f}s", file=sys.stderr)
    enc.stdin.close(); enc.wait()
    print("OK ->", a.out)


if __name__ == "__main__":
    main()
