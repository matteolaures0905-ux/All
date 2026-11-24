#!/usr/bin/env python3
"""3e son : une scene detaillee par phrase.

  python3 rap3.py --lyrics son3.json --audio son3_brut.m4a --duration 43.9 --hero dark --night --out video.mp4
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import cartoon2 as C
import prison  # noqa: F401
import love as L
from cartoon2 import (W, H, INK, ACC, LW, ease, eob, clamp, shade, vgrad, glow, default_pose, big_text, burst, bubble,
                      paste, bill_img, font)

RIVAL = dict(skin=(232, 186, 146), skin_d=(204, 150, 110), jacket=(250, 210, 40), jacket_d=(210, 170, 20),
             sleeve=(250, 210, 40), sleeve_d=(210, 170, 20), cuff=(30, 30, 40), pants=(250, 210, 40),
             shoe=(250, 250, 250), sole=(220, 220, 230), shoe_acc=(230, 40, 60), hat="cap", hat_col=(230, 40, 60),
             hair=(60, 40, 24), chain=False, patch=False, tee=(250, 250, 250))
BOSS = dict(skin=(176, 120, 84), skin_d=(146, 94, 62), jacket=(60, 20, 80), jacket_d=(40, 12, 56),
            sleeve=(60, 20, 80), sleeve_d=(40, 12, 56), cuff=(250, 250, 250), pants=(30, 20, 40),
            shoe=(20, 20, 24), sole=(40, 40, 48), shoe_acc=(20, 20, 24), hat="short", hat_col=(20, 20, 24),
            hair=(20, 16, 14), chain=True, patch=False, tee=(250, 250, 250))
PAL = dict(skin=(198, 134, 92), skin_d=(166, 104, 66), jacket=(60, 150, 170), jacket_d=(40, 116, 134),
           sleeve=(60, 150, 170), sleeve_d=(40, 116, 134), cuff=(40, 116, 134), pants=(70, 80, 120),
           shoe=(250, 250, 250), sole=(220, 220, 230), shoe_acc=(60, 150, 170), hat="curly", hat_col=(30, 22, 18),
           hair=(30, 22, 18), chain=False, patch=False, tee=(240, 240, 240))


def palm(d, x, y, h, rnd, lean=1):
    pts = [(x + lean * 40 * math.sin(i / 10 * 1.4) * (i / 10) * 2, y - h * i / 10) for i in range(11)]
    for i in range(10):
        d.line([pts[i], pts[i + 1]], fill=INK, width=30 - i)
        d.line([pts[i], pts[i + 1]], fill=(120, 80, 50), width=22 - i)
    tx, ty = pts[-1]
    for a in range(0, 360, 45):
        r = math.radians(a + rnd.randint(-10, 10))
        ex, ey = tx + 190 * math.cos(r), ty + 90 * math.sin(r) + 60
        d.polygon([(tx, ty), (ex, ey), (tx + 120 * math.cos(r + 0.25), ty + 50 * math.sin(r + 0.25) + 30)], fill=(30, 120, 80), outline=INK)
    d.ellipse([tx - 24, ty - 10, tx + 24, ty + 30], fill=(110, 70, 40), outline=INK, width=4)


def scene_beach(rnd):
    img = Image.new("RGBA", (W, H))
    vgrad(img, [(0, (40, 20, 90)), (0.45, (200, 70, 130)), (0.75, (255, 150, 90)), (1, (255, 200, 120))], 0, 1100)
    d = ImageDraw.Draw(img)
    glow(img, 540, 1060, 200, (255, 220, 150), 170)
    d = ImageDraw.Draw(img)
    d.chord([380, 900, 700, 1220], 180, 360, fill=(255, 230, 150))
    vgrad(img, [(0, (40, 90, 160)), (1, (20, 50, 110))], 1060, 1330)
    d = ImageDraw.Draw(img)
    for i in range(10):
        y = 1080 + i * 25
        w = 140 - i * 8
        d.line([540 - w, y, 540 + w, y], fill=(255, 210, 140), width=6)
    for i in range(14):
        x, y = rnd.randint(0, W), rnd.randint(1080, 1320)
        d.arc([x - 40, y - 10, x + 40, y + 10], 200, 340, fill=(140, 190, 240), width=4)
    vgrad(img, [(0, (240, 200, 140)), (1, (210, 160, 100))], 1330, H)
    d = ImageDraw.Draw(img)
    d.line([0, 1330, W, 1330], fill=INK, width=LW)
    for k in range(4):  # ecume
        d.arc([k * 300 - 80, 1300, k * 300 + 220, 1360], 0, 180, fill=(250, 250, 255), width=8)
    for x, h, ln in ((70, 820, 1), (990, 760, -1)):
        palm(d, x, 1500, h, rnd, ln)
    for _ in range(25):
        x, y = rnd.randint(0, W), rnd.randint(1380, H)
        d.ellipse([x - 4, y - 3, x + 4, y + 3], fill=(190, 140, 90))
    return img


def scene_pitch(rnd):
    img = Image.new("RGBA", (W, H))
    vgrad(img, [(0, (10, 14, 40)), (1, (40, 40, 90))], 0, 1150)
    d = ImageDraw.Draw(img)
    for x in (90, 990):  # pylones d'eclairage
        d.rectangle([x - 10, 520, x + 10, 1150], fill=(60, 60, 80), outline=INK, width=4)
        d.rectangle([x - 90, 460, x + 90, 540], fill=(70, 70, 90), outline=INK, width=6)
        for k in range(4):
            for j in range(2):
                d.ellipse([x - 78 + k * 42, 470 + j * 34, x - 50 + k * 42, 498 + j * 34], fill=(255, 250, 220))
        glow(img, x, 500, 140, (255, 250, 220), 110)
        d = ImageDraw.Draw(img)
    for i in range(30):  # haie du jardin + maison au fond
        x = i * 40
        d.ellipse([x - 40, 1060, x + 40, 1170], fill=(20, 70, 50), outline=INK, width=4)
    d.rectangle([380, 880, 760, 1080], fill=(80, 60, 90), outline=INK, width=LW)
    d.polygon([(360, 880), (780, 880), (570, 760)], fill=(60, 40, 70), outline=INK)
    for x in (420, 520, 620):
        d.rectangle([x, 930, x + 70, 1010], fill=(255, 220, 140), outline=INK, width=4)
    for i, y in enumerate(range(1150, H, 90)):  # pelouse rayee
        d.rectangle([0, y, W, y + 90], fill=(50, 150, 70) if i % 2 else (40, 130, 60))
    d.line([0, 1150, W, 1150], fill=INK, width=LW)
    d.line([0, 1600, W, 1600], fill=(240, 240, 240), width=8)
    d.arc([340, 1500, 740, 1700], 180, 360, fill=(240, 240, 240), width=8)
    # but
    gx = 760
    d.rectangle([gx, 1180, gx + 300, 1500], outline=(250, 250, 250), width=14)
    for x in range(gx, gx + 300, 30):
        d.line([x, 1180, x + 30, 1500], fill=(200, 200, 220), width=2)
    for y in range(1180, 1500, 30):
        d.line([gx, y, gx + 300, y], fill=(200, 200, 220), width=2)
    return img


def scene_canyon(rnd):
    img = Image.new("RGBA", (W, H))
    vgrad(img, [(0, (30, 20, 70)), (0.6, (180, 80, 110)), (1, (255, 170, 110))], 0, 1300)
    d = ImageDraw.Draw(img)
    vgrad(img, [(0, (60, 30, 60)), (1, (10, 6, 20))], 1300, H)
    d = ImageDraw.Draw(img)
    # deux falaises
    d.polygon([(0, 1240), (300, 1240), (330, 1400), (290, 1700), (320, H), (0, H)], fill=(150, 80, 60), outline=INK)
    d.polygon([(W, 1240), (780, 1240), (750, 1380), (800, 1650), (760, H), (W, H)], fill=(150, 80, 60), outline=INK)
    for y in range(1290, H, 90):
        d.line([20, y, 260, y + 10], fill=(120, 60, 46), width=6)
        d.line([800, y, W - 20, y + 10], fill=(120, 60, 46), width=6)
    d.rectangle([0, 1220, 300, 1250], fill=(90, 150, 80), outline=INK, width=5)
    d.rectangle([780, 1220, W, 1250], fill=(90, 150, 80), outline=INK, width=5)
    return img


def scene_club(rnd):
    img = C.scene_street(rnd)
    d = ImageDraw.Draw(img)
    d.rectangle([250, 700, 830, 1275], fill=(26, 14, 40), outline=INK, width=LW)
    d.rectangle([420, 960, 660, 1275], fill=(120, 40, 150), outline=INK, width=LW)
    d.ellipse([620, 1100, 640, 1120], fill=ACC)
    C.neon(img, (330, 760, 750, 900), "CLUB", (230, 80, 255))
    d = ImageDraw.Draw(img)
    for x in (340, 740):  # poteaux + corde de velours
        d.rectangle([x - 10, 1400, x + 10, 1560], fill=ACC, outline=INK, width=4)
        d.ellipse([x - 20, 1380, x + 20, 1415], fill=ACC, outline=INK, width=4)
    d.arc([340, 1380, 740, 1520], 0, 180, fill=(200, 30, 60), width=16)
    return img


C.SCENES.update(beach=(scene_beach, 1720), pitch=(scene_pitch, 1700), canyon=(scene_canyon, 1235), club=(scene_club, 1700))
C.TOP_TINT.update(beach=(30, 14, 60), pitch=(8, 10, 30), canyon=(24, 14, 50), club=(24, 10, 52))


# ====================================================================== accessoires
def duffel(d, x, y, open_k=0.0):
    d.rounded_rectangle([x - 190, y - 90, x + 190, y + 90], 60, fill=(26, 26, 32), outline=INK, width=LW)
    d.line([x - 150, y - 60, x + 150 - 300 * open_k, y - 60], fill=ACC, width=8)
    d.arc([x - 110, y - 200, x + 110, y - 40], 200, 340, fill=INK, width=18)
    d.arc([x - 110, y - 200, x + 110, y - 40], 200, 340, fill=(50, 50, 60), width=10)
    d.rounded_rectangle([x - 60, y - 10, x + 60, y + 40], 10, fill=(40, 40, 50), outline=(90, 90, 110), width=4)
    d.line([x - 150, y - 50, x - 60, y - 70], fill=(80, 84, 100), width=6)


def shell(d, x, y, ang, s=1.0):
    """Cartouche de fusil a pompe : tube rouge + culot laiton."""
    ca, sa = math.cos(ang), math.sin(ang)
    def R(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    d.polygon([R(-14, -40), R(14, -40), R(14, 22), R(-14, 22)], fill=(210, 30, 45), outline=INK)
    d.line([R(-6, -34), R(-6, 16)], fill=(255, 120, 130), width=max(2, int(5 * s)))
    d.polygon([R(-16, 22), R(16, 22), R(16, 42), R(-16, 42)], fill=(230, 180, 60), outline=INK)
    d.line([R(-16, 30), R(16, 30)], fill=(170, 120, 30), width=3)
    d.line([R(-14, -40), R(14, -40)], fill=(150, 20, 30), width=4)


def pump_gun(d, x, y, s=1.0):
    """Fusil a pompe pose a plat (dessin cartoon)."""
    def r(a, b, c_, e, fill, rad=6):
        d.rounded_rectangle([x + a * s, y + b * s, x + c_ * s, y + e * s], int(rad * s), fill=fill, outline=INK, width=max(3, int(5 * s)))
    wood, wood_d, metal, metal_d = (150, 92, 50), (116, 68, 36), (70, 74, 86), (44, 46, 56)
    r(-60, -10, 360, 14, metal)                     # canon
    r(-40, 16, 300, 34, metal_d)                     # tube magasin
    r(110, 8, 250, 46, wood, 12)                      # pompe
    for k in range(5):
        d.line([x + (130 + k * 24) * s, y + 14 * s, x + (130 + k * 24) * s, y + 40 * s], fill=wood_d, width=max(2, int(4 * s)))
    r(-200, -24, -40, 40, metal)                     # carcasse
    d.ellipse([x - 150 * s, y - 4 * s, x - 120 * s, y + 20 * s], fill=metal_d, outline=INK, width=3)
    d.arc([x - 190 * s, y + 26 * s, x - 120 * s, y + 90 * s], 0, 180, fill=INK, width=max(3, int(7 * s)))   # pontet
    d.polygon([(x - 200 * s, y - 20 * s), (x - 420 * s, y + 10 * s), (x - 430 * s, y + 90 * s), (x - 190 * s, y + 40 * s)], fill=wood, outline=INK)  # crosse
    d.line([(x - 260 * s, y + 6 * s), (x - 400 * s, y + 30 * s)], fill=(190, 130, 80), width=max(2, int(6 * s)))
    d.rounded_rectangle([x - 440 * s, y + 4 * s, x - 418 * s, y + 96 * s], int(6 * s), fill=(30, 30, 36), outline=INK, width=3)
    d.ellipse([x + 340 * s, y - 20 * s, x + 352 * s, y - 8 * s], fill=(230, 230, 240))                    # guidon
    d.line([x - 50 * s, y - 4 * s, x + 340 * s, y - 4 * s], fill=(130, 136, 152), width=max(2, int(4 * s)))  # reflet


def open_bag(d, x, y, t):
    """Sac de sport ouvert, rempli de cartouches."""
    d.rounded_rectangle([x - 200, y - 90, x + 200, y + 100], 60, fill=(26, 26, 32), outline=INK, width=LW)
    d.ellipse([x - 170, y - 120, x + 170, y - 40], fill=(8, 8, 12), outline=INK, width=6)
    rnd = random.Random(7)
    for i in range(11):  # cartouches qui depassent de l'ouverture
        sx = x - 140 + i * 28 + rnd.randint(-6, 6)
        sy = y - 100 + rnd.randint(-14, 10)
        shell(d, sx, sy, math.radians(rnd.randint(-30, 30)), 0.9)
    for k in (-1, 1):  # fermeture eclair ouverte
        d.line([x + k * 175, y - 70, x + k * 120, y - 112], fill=ACC, width=8)
    d.arc([x - 110, y - 230, x + 110, y - 70], 200, 340, fill=INK, width=18)
    d.arc([x - 110, y - 230, x + 110, y - 70], 200, 340, fill=(50, 50, 60), width=10)
    d.rounded_rectangle([x - 60, y + 10, x + 60, y + 60], 10, fill=(40, 40, 50), outline=(90, 90, 110), width=4)
    for i, (dx, dy, a) in enumerate(((-260, 70, 80), (240, 85, -70), (290, 60, 100))):  # quelques cartouches tombees
        shell(d, x + dx, y + dy, math.radians(a), 0.9)


def police_lights(fr, t, strength=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    on = int(t * 6) % 2
    a = int(150 * strength)
    ld.ellipse([-300, 300, 400, 1200], fill=((255, 30, 50) if on else (30, 80, 255)) + (a,))
    ld.ellipse([680, 300, 1380, 1200], fill=((30, 80, 255) if on else (255, 30, 50)) + (a,))
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(120)))


def ledger(fr, c, lt):
    d = ImageDraw.Draw(fr)
    y = c["gy"] - 360
    d.rounded_rectangle([60, y, 1020, y + 60], 12, fill=(120, 76, 46), outline=INK, width=6)
    for lx in (110, 970):
        d.rectangle([lx - 14, y + 60, lx + 14, c["gy"] + 20], fill=(90, 56, 34), outline=INK, width=4)
    bx, by = 540, y - 20
    d.polygon([(bx - 230, by), (bx + 230, by), (bx + 260, by - 150), (bx - 200, by - 150)], fill=(250, 246, 230), outline=INK)
    d.line([bx + 15, by, bx + 30, by - 150], fill=(200, 190, 170), width=4)
    n = int(lt * 6)
    for i in range(min(n, 5)):  # lignes de chiffres qui s'ecrivent
        yy = by - 125 + i * 24
        d.text((bx - 190 + i * 3, yy), "".join(random.Random(i).choice("0123456789") for _ in range(6)), font=font(22), fill=(30, 30, 60))
        d.text((bx + 50 + i * 4, yy), "".join(random.Random(i + 9).choice("0123456789") for _ in range(5)), font=font(22), fill=(30, 30, 60))
    d.rounded_rectangle([780, by - 150, 920, by - 5], 14, fill=(60, 64, 76), outline=INK, width=6)
    d.rectangle([800, by - 135, 900, by - 105], fill=(170, 230, 170))
    for r in range(3):
        for cc in range(3):
            d.rectangle([800 + cc * 35, by - 95 + r * 28, 825 + cc * 35, by - 75 + r * 28], fill=(200, 200, 210))


def chart_down(fr, x, y, k):
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle([x - 200, y - 160, x + 200, y + 160], 18, fill=(250, 250, 255), outline=INK, width=6)
    pts = [(x - 170 + i * 50, y - 100 + (i * 23 + (30 if i % 2 else 0)) * k) for i in range(8)]
    d.line(pts, fill=(230, 40, 60), width=10)
    tx, ty = pts[-1]
    d.polygon([(tx, ty + 30), (tx - 26, ty - 6), (tx + 22, ty - 14)], fill=(230, 40, 60))


def steam(fr, x, y, t):
    d = ImageDraw.Draw(fr)
    for i in range(3):
        ph = (t * 1.5 + i / 3) % 1
        for k in (-1, 1):
            xx, yy = x + k * (120 + 40 * ph), y - 60 - 160 * ph
            r = 20 + 30 * ph
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(235, 235, 240), outline=INK, width=3)


def mystery_box(d, x, y, t):
    d.rounded_rectangle([x - 120, y - 120, x + 120, y + 120], 20, fill=(20, 18, 30), outline=ACC, width=8)
    d.text((x, y), "?", font=font(150), fill=ACC, anchor="mm")
    d.polygon([(x + 60, y - 150), (x + 170, y - 150), (x + 150, y - 90), (x + 50, y - 95)], fill=(255, 60, 90), outline=INK)
    d.text((x + 110, y - 120), "NEW", font=font(36), fill=(255, 255, 255), anchor="mm")
    d.polygon([(x - 160, y + 120), (x + 160, y + 120), (x + 190, y + 200), (x - 190, y + 200)], fill=(60, 60, 80), outline=INK)


def atm(d, x, y, t):
    d.rounded_rectangle([x - 150, y - 260, x + 150, y + 260], 20, fill=(90, 96, 120), outline=INK, width=LW)
    d.rectangle([x - 110, y - 210, x + 110, y - 60], fill=(20, 40, 70), outline=INK, width=6)
    on = int(t * 4) % 2
    d.text((x, y - 135), "0,00 €", font=font(54), fill=(255, 70, 80) if on else (140, 40, 50), anchor="mm")
    for r in range(3):
        for cc in range(3):
            d.rectangle([x - 80 + cc * 55, y - 20 + r * 45, x - 40 + cc * 55, y + 15 + r * 45], fill=(200, 204, 220), outline=INK, width=3)
    d.rectangle([x - 90, y + 170, x + 90, y + 190], fill=INK)


def glass(d, x, y, ang, full=0.0):
    pts = [(-40, -80), (40, -80), (25, 80), (-25, 80)]
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
    d.polygon(P, fill=(200, 230, 255), outline=INK)
    d.line(P + [P[0]], fill=INK, width=6)


def plane(d, x, y, s=1.0):
    d.rounded_rectangle([x - 220 * s, y - 40 * s, x + 220 * s, y + 40 * s], int(40 * s), fill=(240, 244, 255), outline=INK, width=6)
    d.polygon([(x - 40 * s, y), (x + 60 * s, y), (x - 80 * s, y + 160 * s), (x - 140 * s, y + 160 * s)], fill=(220, 226, 240), outline=INK)
    d.polygon([(x - 200 * s, y - 20 * s), (x - 160 * s, y - 20 * s), (x - 220 * s, y - 120 * s), (x - 250 * s, y - 120 * s)], fill=(230, 60, 80), outline=INK)
    for k in range(6):
        d.ellipse([x - 120 * s + k * 50 * s, y - 16 * s, x - 96 * s + k * 50 * s, y + 6 * s], fill=(60, 120, 200))


def villa(d, x, y):
    d.rectangle([x - 360, y - 330, x + 360, y], fill=(250, 246, 236), outline=INK, width=LW)
    d.rectangle([x - 420, y - 360, x + 420, y - 320], fill=(230, 226, 216), outline=INK, width=LW)
    d.rectangle([x - 200, y - 560, x + 260, y - 360], fill=(250, 246, 236), outline=INK, width=LW)
    d.rectangle([x - 240, y - 590, x + 300, y - 555], fill=(230, 226, 216), outline=INK, width=LW)
    for wx in (-320, -140, 40, 220):
        d.rectangle([x + wx, y - 280, x + wx + 120, y - 60], fill=(255, 210, 120), outline=INK, width=5)
    for wx in (-160, 40):
        d.rectangle([x + wx, y - 520, x + wx + 160, y - 400], fill=(255, 210, 120), outline=INK, width=5)
    d.rounded_rectangle([x - 380, y + 20, x + 380, y + 110], 40, fill=(60, 200, 230), outline=INK, width=LW)
    d.line([x - 300, y + 50, x - 100, y + 50], fill=(200, 250, 255), width=6)


def firework(fr, x, y, ph, col):
    if ph <= 0 or ph >= 1:
        return
    d = ImageDraw.Draw(fr)
    r = 40 + 220 * ease(ph)
    for i in range(14):
        a = i * math.tau / 14
        x1, y1 = x + r * 0.6 * math.cos(a), y + r * 0.6 * math.sin(a) + 30 * ph
        x2, y2 = x + r * math.cos(a), y + r * math.sin(a) + 50 * ph
        d.line([x1, y1, x2, y2], fill=col, width=int(10 * (1 - ph)) + 2)
        d.ellipse([x2 - 7, y2 - 7, x2 + 7, y2 + 7], fill=(255, 255, 230))
    glow(fr, x, y, 80 * (1 - ph) + 10, col, int(160 * (1 - ph)))


def castle(d, x, y):
    sand, dk = (236, 196, 130), (200, 156, 90)
    d.rectangle([x - 300, y - 320, x + 300, y], fill=sand, outline=INK, width=LW)
    for tx in (-300, 300):
        d.rectangle([x + tx - 90, y - 520, x + tx + 90, y], fill=sand, outline=INK, width=LW)
        for k in range(3):
            d.rectangle([x + tx - 90 + k * 70, y - 570, x + tx - 50 + k * 70, y - 520], fill=sand, outline=INK, width=5)
        d.polygon([(x + tx - 100, y - 570), (x + tx + 100, y - 570), (x + tx, y - 720)], fill=(230, 60, 80), outline=INK)
        d.line([x + tx, y - 720, x + tx, y - 800], fill=INK, width=6)
        d.polygon([(x + tx, y - 800), (x + tx + 70, y - 780), (x + tx, y - 760)], fill=ACC, outline=INK)
    d.rectangle([x - 120, y - 520, x + 120, y - 320], fill=sand, outline=INK, width=LW)
    d.polygon([(x - 130, y - 520), (x + 130, y - 520), (x, y - 700)], fill=(60, 120, 230), outline=INK)
    d.chord([x - 80, y - 200, x + 80, y + 60], 180, 360, fill=(90, 60, 40), outline=INK, width=6)
    for wx in (-200, 160):
        d.rectangle([x + wx, y - 230, x + wx + 50, y - 160], fill=(255, 220, 130), outline=INK, width=4)
    for i in range(6):
        d.line([x - 280 + i * 100, y - 40, x - 240 + i * 100, y - 60], fill=dk, width=5)


def ball(d, x, y, r, rot):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 250, 250), outline=INK, width=5)
    for i in range(5):
        a = rot + i * math.tau / 5
        px, py = x + r * 0.55 * math.cos(a), y + r * 0.55 * math.sin(a)
        d.ellipse([px - r * 0.22, py - r * 0.22, px + r * 0.22, py + r * 0.22], fill=INK)
    d.ellipse([x - r * 0.25, y - r * 0.25, x + r * 0.25, y + r * 0.25], fill=INK)


def trophy(d, x, y, s=1.0):
    g, gd = (255, 205, 60), (210, 150, 20)
    d.chord([x - 130 * s, y - 330 * s, x + 130 * s, y - 70 * s], 0, 180, fill=g, outline=INK, width=6)
    d.rectangle([x - 130 * s, y - 330 * s, x + 130 * s, y - 200 * s], fill=g, outline=INK, width=6)
    d.rectangle([x - 124 * s, y - 330 * s, x + 124 * s, y - 210 * s], fill=g)
    for k in (-1, 1):
        d.arc([x + k * 130 * s - 60 * s, y - 310 * s, x + k * 130 * s + 60 * s, y - 170 * s], 270 if k == 1 else 90, 90 if k == 1 else 270, fill=gd, width=int(16 * s))
    d.rectangle([x - 25 * s, y - 75 * s, x + 25 * s, y], fill=gd, outline=INK, width=5)
    d.rounded_rectangle([x - 100 * s, y, x + 100 * s, y + 60 * s], int(10 * s), fill=(60, 40, 30), outline=INK, width=6)
    d.line([x - 80 * s, y - 300 * s, x - 60 * s, y - 120 * s], fill=(255, 250, 200), width=int(10 * s))


def mask(d, x, y, k, fall):
    """Masque souriant qui tombe et revele une grimace."""
    dy = 700 * ease(fall)
    ang = 40 * fall
    d.ellipse([x - 60, y - 70, x + 60, y + 70], fill=(120, 200, 140), outline=INK, width=5)
    for e in (-1, 1):
        d.line([x + e * 30 - 14, y - 26 + e * 4, x + e * 30 + 14, y - 26 - e * 4], fill=INK, width=6)
    d.arc([x - 30, y + 20, x + 30, y + 50], 200, 340, fill=INK, width=6)
    if fall < 1:
        mx, my = x + 30 * fall, y + dy
        d.ellipse([mx - 70, my - 80, mx + 70, my + 80], fill=(250, 246, 236), outline=INK, width=6)
        for e in (-1, 1):
            d.ellipse([mx + e * 28 - 14, my - 30, mx + e * 28 + 14, my - 6], fill=INK)
        d.chord([mx - 40, my + 6, mx + 40, my + 56], 0, 180, fill=(230, 60, 80), outline=INK, width=5)


# ====================================================================== actions (1 par phrase)
def P(**kw):
    def f(t, talk):
        p = default_pose(t, talk)
        p.update({k: (v(t) if callable(v) and k not in ("rh_prop", "lh_prop") else v) for k, v in kw.items()})
        return p
    return f


def sprite(fn, size, *args):
    """Dessine fn(d, cx, cy, *args) sur un calque transparent centre."""
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), size[0] // 2, size[1] // 2, *args)
    return im


_gun = {}
def prop_shotgun(fr, Cp, s, t):
    """Fusil a pompe tenu en travers de la poitrine, canon vers le ciel."""
    key = round(s, 2)
    if key not in _gun:
        sc = 0.7 * s
        im = Image.new("RGBA", (1400, 1400), (0, 0, 0, 0))
        pump_gun(ImageDraw.Draw(im), 700 + 160 * sc, 700 - 30 * sc, sc)  # la poignee tombe au centre du calque
        _gun[key] = im.rotate(58, resample=Image.BICUBIC)
    g = _gun[key]
    fr.alpha_composite(g, (int(Cp[0] - g.width / 2), int(Cp[1] - g.height / 2)))


_bag = {}
def prop_bag(fr, Cp, s, t):
    """Sac de cartouches qui pend a la main."""
    key = round(s, 2)
    if key not in _bag:
        im = Image.new("RGBA", (760, 600), (0, 0, 0, 0))
        open_bag(ImageDraw.Draw(im), 380, 360, 0)
        _bag[key] = im.resize((int(760 * 0.62 * s), int(600 * 0.62 * s)), Image.LANCZOS)
    b = _bag[key]
    sway = 4 * math.sin(t * 3)
    fr.alpha_composite(b, (int(Cp[0] - b.width / 2 + sway), int(Cp[1] - 40 * s)))


def A1(c):  # le heros tient le fusil a pompe et le sac de cartouches
    lt = c["lt"]
    def back(fr, c):
        L.supercar(fr, 700, c["gy"] - 320, 0.95, col=(40, 120, 200))
        glow(fr, 380, c["gy"] - 620, 200, ACC, int(50 + 90 * C.VOC[0]))
    hero = P(rh=(110, -470), rh_shape="fist", rh_prop=prop_shotgun, lh=(-200, -300), lh_shape="fist", lh_prop=prop_bag,
             look=(0, 0), brows="angry", mouth="flat", shades=0)
    return dict(hero=hero, hx=380, back=back)


def A2(c):  # sirenes : c'est le rival qui cavale, le heros reste calme
    lt = c["lt"]
    rx = 1150 - 1350 * ease(lt / 1.8)
    def rival(t, talk):
        sw = math.sin(t * 16)
        p = default_pose(t, 0, 1)
        p.update(walk=1.4, lh=(-170 + 90 * sw, -380), rh=(170 - 90 * sw, -380), look=(-1, 0), brows="up", mouth="o", bob=8 * abs(sw))
        return p
    def back(fr, c):
        police_lights(fr, c["t"], 0.7)
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(5):  # traits de vitesse derriere le rival
            y = c["gy"] - 200 - i * 110
            d.line([rx + 170, y, rx + 360 + i * 25, y], fill=(255, 255, 255), width=6)
        big_text(fr, 760, c["gy"] - 1080, "WIOU WIOU", 80, eob((lt - 0.2) / 0.3), ang=8, col=(120, 170, 255))
    return dict(hero=P(lh=(70, -430), rh=(-70, -415), shades=1, mouth="smirk", look=(1, 0)), hx=230,
                extras=[dict(x=rx, style=RIVAL, posefn=rival, s=0.86)], back=back, front=front)


def A3(c):  # les comptes au stylo
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(rh=(190 + 30 * math.sin(t * 12), -430), rh_shape="fist", look=(1, 1), brows="angry", mouth="flat" if talk < 0.25 else "talk")
        return p
    def front(fr, c):
        ledger(fr, c, lt)
        d = ImageDraw.Draw(fr)
        x, y = c["hx"] + 0.92 * (190 + 30 * math.sin(c["t"] * 12)), c["gy"] - 0.92 * 430
        d.line([x, y, x + 50, y + 90], fill=INK, width=14)
        d.line([x + 40, y + 72, x + 52, y + 94], fill=(30, 30, 40), width=8)
    return dict(hero=hero, hx=260, front=front)


def A4(c):  # chiffres en baisse, rival enerve
    lt = c["lt"]
    def rival(t, talk):
        p = default_pose(t, 0, 1)
        p.update(lh=(-120, -720), rh=(120, -720), lh_shape="fist", rh_shape="fist", brows="angry", mouth="frown", eyes="closed")
        return p
    def front(fr, c):
        chart_down(fr, 330, 760, ease(lt / 0.8))
        steam(fr, 740, c["gy"] - 0.86 * 760, c["t"])
    return dict(hero=None, extras=[dict(x=740, style=RIVAL, posefn=rival, s=0.86)], front=front)


def A5(c):  # poches vides
    lt = c["lt"]
    def rival(t, talk):
        p = default_pose(t, 0, 1)
        p.update(lh=(-190, -330), rh=(190, -330), lh_shape="open", rh_shape="open", brows="sad", mouth="o", look=(0, 1))
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        x0 = 700
        for k in (-1, 1):  # poches retournees
            px, py = x0 + k * 0.86 * 120, c["gy"] - 0.86 * 300
            d.polygon([(px - 40, py), (px + 40, py), (px + 30, py + 70), (px - 30, py + 70)], fill=(240, 240, 240), outline=INK)
        ph = clamp((lt - 0.3) / 1.2)
        mx, my = x0 + 60 + 200 * ph, c["gy"] - 300 - 500 * ph
        fl = math.sin(c["t"] * 30) * 18
        d.polygon([(mx, my), (mx - 40, my - 20 - fl), (mx - 30, my + 20)], fill=(200, 190, 170), outline=INK)
        d.polygon([(mx, my), (mx + 40, my - 20 - fl), (mx + 30, my + 20)], fill=(200, 190, 170), outline=INK)
        d.ellipse([mx - 8, my - 16, mx + 8, my + 16], fill=(120, 100, 80))
    return dict(hero=P(lh=(70, -430), rh=(-70, -415), look=(1, 0), mouth="smirk", brows="skeptic"), hx=260,
                extras=[dict(x=700, style=RIVAL, posefn=rival, s=0.86)], front=front)


def A6(c):  # il frime devant elle
    lt = c["lt"]
    def rival(t, talk):
        p = default_pose(t, 0, 1)
        p.update(rh=(150, -720), rh_shape="fist", lh=(-150, -560), lh_shape="open", mouth="smile", brows="up", look=(1, 0))
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        rx, ry = 480 - 0.82 * 150, c["gy"] - 0.82 * 560
        d.line([rx, ry, rx - 10, ry + 90], fill=(40, 140, 60), width=8)
        for a in range(0, 360, 60):
            r = math.radians(a + c["t"] * 40)
            d.ellipse([rx + 22 * math.cos(r) - 22, ry - 20 + 22 * math.sin(r) - 22, rx + 22 * math.cos(r) + 22, ry - 20 + 22 * math.sin(r) + 22], fill=(230, 40, 70), outline=INK, width=3)
        for i in range(3):
            a = c["t"] * 4 + i * 2
            x, y = 480 + 150 * math.cos(a), c["gy"] - 900 + 40 * math.sin(a)
            d.line([x - 14, y, x + 14, y], fill=(255, 250, 200), width=5); d.line([x, y - 14, x, y + 14], fill=(255, 250, 200), width=5)
    return dict(hero=P(look=(1, -1), eyes="sleepy", mouth="flat", lh=(70, -430), rh=(-70, -415)), hx=170,
                extras=[dict(x=480, style=RIVAL, posefn=rival, s=0.82), dict(x=850, style=L.GIRL, posefn=L.girl_pose("doubt", lt), s=0.82)], front=front)


def A7(c):  # la boite de nuit ? non
    lt = c["lt"]
    walk = lt > 0.8
    hx = 540 + 500 * ease((lt - 0.8) / 1.2)
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = eob((lt - 0.3) / 0.3)
        if k > 0.05:
            x, y, r = 540, 830, 150 * k
            d.line([x - r, y - r, x + r, y + r], fill=INK, width=int(46 * k) + 1)
            d.line([x + r, y - r, x - r, y + r], fill=INK, width=int(46 * k) + 1)
            d.line([x - r, y - r, x + r, y + r], fill=(255, 50, 70), width=int(30 * k) + 1)
            d.line([x + r, y - r, x - r, y + r], fill=(255, 50, 70), width=int(30 * k) + 1)
    return dict(hero=P(lh=(-170 + (60 if walk else 0) * 1, -330), rh=(-60, -560), rh_shape="open", walk=1 if walk else 0, mouth="smirk", look=(1, 0)),
                hx=hx, front=front)


def A8(c):  # le patron et son cheque
    lt = c["lt"]
    def boss(t, talk):
        p = default_pose(t, 0, 2)
        p.update(lh=(-260, -520), lh_shape="open", mouth="smile", brows="up", look=(-1, 0))
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = eob((lt - 0.2) / 0.3)
        if k > 0.05:
            x, y = 560, c["gy"] - 640
            d.rounded_rectangle([x - 170 * k, y - 80 * k, x + 170 * k, y + 80 * k], int(10 * k), fill=(230, 250, 230), outline=INK, width=6)
            d.text((x, y - 10 * k), "15 000 €", font=font(int(70 * k) + 1), fill=(30, 120, 50), anchor="mm")
            d.line([x - 130 * k, y + 50 * k, x + 40 * k, y + 50 * k], fill=(60, 60, 80), width=4)
        if lt > 0.7:
            burst(d, 560, c["gy"] - 640, 3.0, ACC)
    return dict(hero=P(rh=(240, -560), rh_shape="open", shades=lambda t: ease((lt - 0.6) / 0.4), mouth="smile", look=(1, 0)), hx=260,
                extras=[dict(x=820, style=BOSS, posefn=boss, s=0.95)], front=front)


def A9(c):  # boite mystere
    lt = c["lt"]
    def back(fr, c):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(680, 380), (760, 380), (960, c["gy"] - 250), (480, c["gy"] - 250)], fill=(255, 240, 180, int(70 + 70 * C.VOC[0])))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
        d = ImageDraw.Draw(fr)
        mystery_box(d, 720, c["gy"] - 560 + 10 * math.sin(c["t"] * 3), c["t"])
        for i in range(3):  # fleches de croissance
            k = ease((lt - 0.2 - i * 0.2) / 0.4)
            x0, y0 = 120 + i * 120, 1000
            d.line([x0, y0, x0 + 80 * k, y0 - 200 * k], fill=(120, 230, 140), width=14)
            if k > 0.9:
                d.polygon([(x0 + 80, y0 - 230), (x0 + 50, y0 - 190), (x0 + 105, y0 - 185)], fill=(120, 230, 140), outline=INK)
    return dict(hero=P(lh=(-40, -760), lh_shape="point", rh=(260, -560), rh_shape="open", mouth="smile", shades=1, look=(1, 0)), hx=300, back=back)


def A10(c):  # mystere : que les yeux
    lt = c["lt"]
    def pre(fr, c):
        pass
    def front(fr, c):
        lay = Image.new("RGBA", (W, H), (6, 4, 14, 0))
        ld = ImageDraw.Draw(lay)
        ld.rectangle([0, 0, W, H], fill=(6, 4, 14, 215))
        fr.alpha_composite(lay)
        # seuls les yeux du heros restent visibles
        for k in (-1, 1):
            ex, ey = 540 + 0.92 * 40 * k, c["gy"] - 0.92 * 695 - 0.92 * 6 * math.sin(c["t"] * 6)
            C.glow(fr, ex, ey, 50, (255, 176, 20), int(180 + 70 * C.VOC[0]))
            d = ImageDraw.Draw(fr)
            d.ellipse([ex - 28, ey - 14, ex + 28, ey + 14], fill=(255, 190, 40), outline=INK, width=4)
            d.ellipse([ex - 4, ey - 13, ex + 4, ey + 13], fill=INK)
        d = ImageDraw.Draw(fr)
        for i, (x, y) in enumerate(((180, 900), (900, 860), (250, 1300), (860, 1350))):
            big_text(fr, x, y, "?", 120, eob((lt - 0.2 - i * 0.15) / 0.3), ang=(-1) ** i * 10, col=(200, 200, 230))
    return dict(hero=P(lh=(70, -430), rh=(-70, -415), mouth="smirk"), hx=540, extras=[dict(x=x_, seed=40 + i, pose="listen") for i, x_ in enumerate((120, 960))], front=front)


def A11(c):  # pour toujours ?
    lt = c["lt"]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = eob((lt - 0.2) / 0.3)
        x, y = 540, c["gy"] - 1060
        if k > 0.05:  # coeur + infini
            L.heart(d, x, y, 110 * k * (1 + 0.08 * C.VOC[0]))
            pts = [(x + 150 * k * math.sin(a), y + 230 * k + 60 * k * math.sin(a) * math.cos(a)) for a in [i * math.tau / 60 for i in range(61)]]
            d.line(pts, fill=ACC, width=12)
        big_text(fr, 880, y + 40, "?", 140, eob((lt - 0.6) / 0.3), ang=12, col=(255, 255, 255))
    return dict(hero=P(lh=(160, -480), lh_shape="open", look=(1, 0), mouth="smile"), hx=330,
                extras=[dict(x=760, style=L.GIRL, posefn=L.girl_pose("love", lt), s=0.86)], front=front)


def A12(c):  # verres renverses, distributeur a zero
    lt = c["lt"]
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        atm(d, 800, c["gy"] - 560, c["t"])
        y = c["gy"] - 360
        d.rounded_rectangle([40, y, 520, y + 40], 10, fill=(150, 100, 70), outline=INK, width=6)
        for i in range(3):
            ang = math.radians(90 * ease((lt - 0.2 - i * 0.2) / 0.4)) * (-1 if i % 2 else 1)
            glass(d, 130 + i * 140, y - 80 + 40 * abs(math.sin(ang)), ang)
    return dict(hero=P(rh=(240, -720), rh_shape="open", brows="sad", mouth="frown", look=(1, 0)), hx=420, back=back)


def A13(c):  # non merci
    lt = c["lt"]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = eob((lt - 0.15) / 0.3)
        x, y, r = 540, c["gy"] - 1080, 120 * k
        if k > 0.05:
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 50, 70), outline=INK, width=8)
            d.line([x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55], fill=(255, 255, 255), width=int(26 * k) + 1)
            d.line([x + r * 0.55, y - r * 0.55, x - r * 0.55, y + r * 0.55], fill=(255, 255, 255), width=int(26 * k) + 1)
    return dict(hero=P(look=lambda t: (math.sin(t * 14), 0), lh=(70, -430), rh=(-70, -415), brows="skeptic", mouth="flat"), hx=540, front=front)


def A14(c):  # il compte, l'avion decolle
    lt = c["lt"]
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        ph = clamp(lt / 1.0)
        plane(d, -200 + 1300 * ph, 760 - 300 * ph, 0.9)
        d.rounded_rectangle([700, 880, 1020, 990], 14, fill=(30, 120, 80), outline=INK, width=6)
        d.text((860, 935), "SOLEIL ->", font=font(56), fill=(255, 255, 255), anchor="mm")
    def front(fr, c):
        b = bill_img()
        x, y = c["hx"] + 0.92 * 120, c["gy"] - 0.92 * 520
        for i in range(4):
            paste(fr, b, x + 10 * math.sin(c["t"] * 12 + i), y - i * 12, ang=(i - 1.5) * 10, k=0.42)
    return dict(hero=P(rh=(120, -520), lh=(-40, -500), look=(0.5, 1), mouth="smile"), hx=280, back=back, front=front)


def A15(c):  # villa et feux d'artifice
    lt = c["lt"]
    def back(fr, c):
        for i, (x, y, col) in enumerate(((240, 620, (255, 90, 160)), (760, 560, (90, 220, 255)), (520, 470, (255, 210, 80)), (880, 760, (180, 120, 255)))):
            firework(fr, x, y, ((lt * 0.9) + i * 0.27) % 1.2, col)
        d = ImageDraw.Draw(fr)
        villa(d, 540, c["gy"] - 260)
    return dict(hero=P(rh=(230, -760), rh_shape="open", lh=(-230, -760), lh_shape="open", shades=1, mouth="smile"), hx=540, hero_s=0.85, back=back)


def A16(c):  # chateau sur la plage
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        castle(d, 650, c["gy"] - 260)
    return dict(hero=P(lh=(-90, -330), rh=(40, -700), rh_shape="point", shades=1, mouth="smile", look=(1, -1)), hx=220, back=back)


def A17(c):  # le bolide rouge, le pote reste a quai
    lt = c["lt"]
    def back(fr, c):
        x = 560 + 600 * ease((lt - 0.9) / 1.0)
        L.supercar(fr, x, c["gy"] - 140, 1.0, col=(220, 30, 40))
        d = ImageDraw.Draw(fr)
        # le heros au volant (tete visible dans la vitre)
        hx_, hy_ = x + 120, c["gy"] - 330
        d.ellipse([hx_ - 40, hy_ - 40, hx_ + 40, hy_ + 40], fill=C.ACTIVE[0]["skin"], outline=INK, width=4)
        d.chord([hx_ - 44, hy_ - 56, hx_ + 44, hy_ + 10], 180, 360, fill=C.ACTIVE[0]["hat_col"], outline=INK, width=4)
        d.rounded_rectangle([hx_ - 34, hy_ - 12, hx_ + 34, hy_ + 4], 6, fill=(18, 14, 26), outline=ACC, width=3)
        d.text((x - 60, c["gy"] - 220), "2", font=font(80), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=INK)
    def pal(t, talk):
        p = default_pose(t, 0, 1)
        p.update(rh=(160 + 40 * math.sin(t * 12), -720), rh_shape="open", brows="sad", mouth="o", look=(1, 0))
        return p
    return dict(hero=None, extras=[dict(x=150, style=PAL, posefn=pal, s=0.8)], back=back)


def A18(c):  # clin d'oeil
    lt = c["lt"]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(6):
            a = c["t"] * 3 + i
            x, y = 540 + 330 * math.cos(a), c["gy"] - 800 + 200 * math.sin(a)
            d.line([x - 18, y, x + 18, y], fill=(255, 240, 160), width=6); d.line([x, y - 18, x, y + 18], fill=(255, 240, 160), width=6)
    return dict(hero=P(rh=(140, -640), rh_shape="point", eyes=lambda t: "closed" if (lt % 1.0) < 0.35 else None, mouth="smile", look=(0, 0)),
                hx=540, hero_s=1.12, hero_gy=1800, front=front)


def A19(c):  # pas de bruit, sur la pelouse
    lt = c["lt"]
    hx = 120 + 520 * ease(lt / 2.3)
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(walk=0.6, lh=(-40, -620), lh_shape="point", rh=(220, -470), rh_shape="open", look=(1, 0), brows="up", mouth="flat", bob=-30)
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        ball(d, hx + 130, c["gy"] - 30, 36, c["t"] * 6)
        big_text(fr, hx - 60, c["gy"] - 1000, "CHUT", 90, eob((lt - 0.3) / 0.3), ang=-8, col=(200, 220, 255))
    return dict(hero=hero, hx=hx, front=front)


def A20(c):  # la coupe est a nous
    lt = c["lt"]
    lift = ease(lt / 0.6)
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        trophy(d, c["hx"], c["gy"] - 720 - 120 * lift, 0.9)
        C.L_conf = None
        rnd = random.Random(5)
        for i in range(30):  # confettis
            ph = (lt * 0.7 + i / 30) % 1
            x = rnd.randint(0, W) + 40 * math.sin(c["t"] * 3 + i)
            y = 300 + 1400 * ph
            col = [(255, 80, 140), (80, 220, 255), (255, 210, 60), (150, 255, 120)][i % 4]
            d.rectangle([x - 8, y - 4, x + 8, y + 4], fill=col)
    return dict(hero=P(lh=(-90, -760 - 100 * lift), rh=(90, -760 - 100 * lift), mouth="smile", shades=1, look=(0, -1)), hx=540, front=front)


def A21(c):  # les masques tombent
    lt = c["lt"]
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i, x in enumerate((140, 330, 750, 940)):
            y = c["gy"] - 0.8 * 695 - 6 * (i % 2)
            mask(d, x, y, 1, clamp((lt - 0.3 - i * 0.25) / 0.6))
    extras = [dict(x=x_, seed=50 + i, pose="listen", look=(1 if x_ < 540 else -1, 0)) for i, x_ in enumerate((140, 330, 750, 940))]
    return dict(hero=P(lh=(70, -430), rh=(-70, -415), brows="angry", mouth="flat", shades=0), hx=540, hero_s=1.05, extras=extras, front=front)


def A22(c):  # le pont cede
    lt = c["lt"]
    cut = 0.6
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        y0 = 1240
        if lt < cut:
            pts = [(300 + i * 24, y0 + 90 * math.sin(math.pi * i / 20)) for i in range(21)]
            d.line(pts, fill=(140, 90, 50), width=14)
            for (x, y) in pts[::2]:
                d.rectangle([x - 12, y - 6, x + 12, y + 14], fill=(170, 110, 60), outline=INK, width=3)
        else:
            k = ease((lt - cut) / 0.6)
            for side in (0, 1):  # les deux moities pendent dans le vide
                ax = 300 if side == 0 else 780
                pts = [(ax + (1 if side == 0 else -1) * i * 24 * (1 - k * 0.9), y0 + i * 24 * k * 1.2) for i in range(11)]
                d.line(pts, fill=(140, 90, 50), width=14)
                for (x, y) in pts[::2]:
                    d.rectangle([x - 12, y - 6, x + 12, y + 14], fill=(170, 110, 60), outline=INK, width=3)
        for x in (300, 780):
            d.rectangle([x - 12, y0 - 80, x + 12, y0 + 10], fill=(110, 70, 40), outline=INK, width=4)
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        x, y = 330, 1080
        o = 0.3 if lt < cut else 0.0
        for k in (-1, 1):  # grands ciseaux
            ang = math.radians(k * (20 + 25 * o * math.sin(c["t"] * 20)))
            d.line([x, y, x + 200 * math.cos(ang), y + 200 * math.sin(ang)], fill=(200, 206, 222), width=18)
            d.ellipse([x - 80 * math.cos(ang) - 34, y - 80 * math.sin(ang) - 24, x - 80 * math.cos(ang) + 34, y - 80 * math.sin(ang) + 24], outline=(255, 90, 110), width=12)
        if lt > cut:
            burst(d, 300, 1240, 1.5, (255, 255, 255))
    extras = [dict(x=x_, seed=60 + i, pose="listen", look=(-1, 0), gy_off=0, s=0.6) for i, x_ in enumerate((870, 1000))]
    return dict(hero=P(rh=(220, -600), rh_shape="fist", brows="angry", mouth="smirk", shades=1, look=(1, 0)), hx=140, hero_s=0.62, extras=extras, back=back, front=front)


C.ACTIONS.update({f"p{i}": f for i, f in enumerate([A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, A21, A22], 1)})

if __name__ == "__main__":
    C.main()
