#!/usr/bin/env python3
"""Extension "prison / evasion" pour cartoon2.py : nouveaux decors et actions.

  python3 prison.py --lyrics son2_prison.json --audio son2_brut.m4a --duration 31.5 --hero dark --night --out video.mp4
"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
import cartoon2 as C
from cartoon2 import W, H, INK, ACC, LW, ease, eob, clamp, shade, vgrad, glow, default_pose, big_text, burst, font

OFFICER = dict(skin=(200, 150, 110), skin_d=(170, 120, 84), jacket=(40, 60, 110), jacket_d=(28, 44, 84),
               sleeve=(40, 60, 110), sleeve_d=(28, 44, 84), cuff=(28, 44, 84), pants=(30, 36, 60),
               shoe=(20, 20, 26), sole=(50, 50, 60), shoe_acc=(20, 20, 26), hat="cap", hat_col=(30, 44, 84),
               hair=(40, 30, 20), chain=False, patch=False, tee=(230, 230, 240))


# ====================================================================== decors
def scene_cell(rnd):
    img = Image.new("RGBA", (W, H), (96, 104, 124))
    d = ImageDraw.Draw(img)
    for y in range(0, 1420, 110):  # blocs de beton
        off = (y // 110) % 2 * 150
        for x in range(-300 + off, W, 300):
            c = rnd.choice([(96, 104, 124), (104, 112, 132), (88, 96, 116)])
            d.rectangle([x + 4, y + 4, x + 296, y + 106], fill=c)
    # fenetre haute a barreaux + lune
    d.rectangle([600, 470, 860, 660], fill=(20, 26, 60), outline=INK, width=LW)
    d.ellipse([740, 500, 810, 570], fill=(250, 240, 210))
    for x in range(630, 860, 52):
        d.line([x, 470, x, 660], fill=(60, 60, 70), width=12)
    # faisceau de lune
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon([(600, 660), (860, 660), (720, 1700), (300, 1700)], fill=(200, 220, 255, 45))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(img)
    # marques au mur (jours comptes)
    for g in range(4):
        gx, gy = 80 + (g % 2) * 150, 760 + (g // 2) * 120
        for k in range(4):
            d.line([gx + k * 22, gy, gx + k * 22, gy + 80], fill=(50, 50, 64), width=7)
        d.line([gx - 10, gy + 70, gx + 80, gy + 10], fill=(50, 50, 64), width=7)
    # fissures
    d.line([(980, 300), (940, 380), (970, 450), (930, 560)], fill=(60, 66, 84), width=5)
    # couchette
    d.rectangle([640, 1150, 1080, 1190], fill=(150, 150, 165), outline=INK, width=6)
    d.rounded_rectangle([650, 1100, 1080, 1155], 16, fill=(214, 120, 70), outline=INK, width=6)
    d.rounded_rectangle([960, 1070, 1070, 1110], 14, fill=(240, 236, 226), outline=INK, width=5)
    for lx in (660, 1060):
        d.rectangle([lx - 10, 1190, lx + 10, 1420], fill=(150, 150, 165), outline=INK, width=4)
    # sol
    vgrad(img, [(0, (70, 74, 92)), (1, (46, 48, 64))], 1420, H)
    d = ImageDraw.Draw(img)
    d.line([0, 1420, W, 1420], fill=INK, width=LW)
    for y in (1520, 1650, 1810):
        d.line([0, y, W, y], fill=(56, 58, 76), width=4)
    return img


def scene_yard(rnd):
    img = Image.new("RGBA", (W, H))
    vgrad(img, [(0, (12, 18, 46)), (0.7, (40, 36, 90)), (1, (90, 60, 110))], 0, 1300)
    d = ImageDraw.Draw(img)
    for _ in range(60):
        x, y = rnd.randint(0, W), rnd.randint(380, 900)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(240, 240, 255))
    # mirador
    d.polygon([(850, 1300), (1010, 1300), (980, 760), (880, 760)], fill=(70, 66, 80), outline=INK)
    for y in (880, 1000, 1120, 1240):
        d.line([862 - (y - 760) * 0.06, y, 998 + (y - 760) * 0.06, y], fill=INK, width=5)
    d.rectangle([840, 660, 1040, 770], fill=(90, 86, 104), outline=INK, width=LW)
    d.rectangle([862, 680, 1018, 740], fill=(255, 220, 140), outline=INK, width=5)
    d.polygon([(820, 660), (1060, 660), (940, 590)], fill=(60, 56, 72), outline=INK)
    # grillage + barbeles
    top = 980
    d.rectangle([-10, top, W + 10, 1320], fill=(54, 58, 80))
    for x in range(-400, W + 400, 44):
        d.line([x, top, x + 340, 1320], fill=(120, 126, 150), width=3)
        d.line([x + 340, top, x, 1320], fill=(120, 126, 150), width=3)
    for x in range(0, W, 220):
        d.rectangle([x - 8, top - 40, x + 8, 1320], fill=(90, 94, 110), outline=INK, width=4)
    for x in range(-40, W + 40, 70):  # spirales de barbele
        d.ellipse([x, top - 80, x + 90, top - 10], outline=(170, 176, 196), width=5)
    d.line([0, top, W, top], fill=INK, width=6)
    # sol de la cour
    vgrad(img, [(0, (92, 84, 92)), (1, (58, 52, 64))], 1320, H)
    d = ImageDraw.Draw(img)
    d.line([0, 1320, W, 1320], fill=INK, width=LW)
    d.rectangle([60, 1450, 260, 1560], fill=(140, 96, 60), outline=INK, width=LW)  # caisse
    d.line([60, 1450, 260, 1560], fill=INK, width=5); d.line([260, 1450, 60, 1560], fill=INK, width=5)
    for y in (1420, 1600, 1780):
        d.line([0, y, W, y], fill=(70, 64, 76), width=4)
    return img


def scene_interro(rnd):
    img = Image.new("RGBA", (W, H), (60, 66, 70))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 160):
        d.line([x, 0, x, 1380], fill=(52, 58, 62), width=6)
    # miroir sans tain
    d.rectangle([120, 560, 960, 1060], fill=(24, 30, 40), outline=INK, width=12)
    d.line([200, 600, 420, 1000], fill=(70, 84, 100), width=18)
    d.line([300, 600, 470, 920], fill=(60, 72, 88), width=8)
    for k, x in enumerate((640, 820)):  # silhouettes derriere la vitre
        d.ellipse([x - 50, 760, x + 50, 860], fill=(38, 46, 58))
        d.rounded_rectangle([x - 90, 850, x + 90, 1060], 50, fill=(38, 46, 58))
    vgrad(img, [(0, (50, 52, 58)), (1, (30, 32, 38))], 1380, H)
    d = ImageDraw.Draw(img)
    d.line([0, 1380, W, 1380], fill=INK, width=LW)
    # lampe suspendue
    d.line([W // 2, 0, W // 2, 380], fill=INK, width=6)
    d.polygon([(W // 2 - 120, 480), (W // 2 + 120, 480), (W // 2 + 60, 380), (W // 2 - 60, 380)], fill=(40, 44, 50), outline=INK)
    return img


C.SCENES.update(cell=(scene_cell, 1700), yard=(scene_yard, 1690), interro=(scene_interro, 1720))
C.TOP_TINT.update(cell=(30, 32, 44), yard=(10, 14, 36), interro=(24, 26, 30))


# ====================================================================== aides
def bars(fr, xs=None, alpha=255):
    d = ImageDraw.Draw(fr)
    xs = xs or range(40, W, 130)
    for x in xs:
        d.rectangle([x - 16, 380, x + 16, H], fill=(36, 38, 48), outline=INK, width=5)
        d.line([x - 6, 400, x - 6, H], fill=(110, 116, 136), width=6)
    for y in (560, 1260):
        d.rectangle([0, y, W, y + 34], fill=(36, 38, 48), outline=INK, width=5)


def lamp_cone(fr, c, swing=True):
    ang = 0.12 * math.sin(c["t"] * 2.4) if swing else 0
    cx, cy = W // 2, 480
    bx = cx + math.tan(ang) * (c["gy"] - cy)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon([(cx - 110, cy), (cx + 110, cy), (bx + 430, c["gy"]), (bx - 430, c["gy"])], fill=(255, 236, 170, 70))
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(fr).ellipse([cx - 50, cy - 16, cx + 50, cy + 16], fill=(255, 245, 200))


def table(fr, c, y):
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle([170, y, 910, y + 50], 10, fill=(150, 156, 170), outline=INK, width=6)
    for lx in (220, 860):
        d.rectangle([lx - 12, y + 50, lx + 12, c["gy"] + 20], fill=(110, 116, 130), outline=INK, width=4)


def searchlight(fr, c, x):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon([(925, 710), (955, 710), (x + 170, c["gy"] + 40), (x - 170, c["gy"] + 40)], fill=(255, 250, 210, 95))
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(fr)
    d.ellipse([x - 190, c["gy"] - 20, x + 190, c["gy"] + 60], outline=(255, 250, 220), width=4)


# ====================================================================== actions
def A_count(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        sc = (t * 3) % 1
        p.update(lh=(-260 + 30 * sc, -640 + 60 * sc), lh_shape="point", look=(-1, 0), eyes="sleepy", mouth="flat" if talk < 0.25 else "talk")
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        n = int(lt * 5)  # nouvelles marques qui s'ajoutent
        for k in range(min(n, 9)):
            x = 90 + (k % 5) * 22
            d.line([x, 1020, x, 1100], fill=(250, 240, 220), width=7)
        bars(fr)
    return dict(hero=hero, hx=420, front=front)


def A_grip(c):
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(-140, -640), rh=(140, -640), brows="angry", mouth="flat" if talk < 0.25 else "talk", look=(0, 0), bob=-4)
        return p
    def front(fr, c):
        bars(fr, xs=[540 - 270, 540 - 140, 540 + 140, 540 + 270, 120, 960])
        d = ImageDraw.Draw(fr)
        for x in (540 - 140, 540 + 140):  # mains par-dessus les barreaux
            y = c["gy"] - 0.92 * 640 - 6
            d.ellipse([x * 1 - 0 - 26, y - 26, x + 26, y + 26], fill=C.ACTIVE[0]["skin"], outline=INK, width=5)
    return dict(hero=hero, hx=540, front=front, hero_s=1.08, hero_gy=1800)


def A_interro(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(70, -430), rh=(-70, -415), shades=ease((lt - 0.3) / 0.4), mouth="smirk", look=(1, 0))
        return p
    def officer(t, talk):
        p = default_pose(t, 0, 2)
        jab = math.sin(t * 9) * 30
        p.update(lh=(-300 + jab, -560), lh_shape="point", brows="angry", mouth="talk", talk=0.4 + 0.3 * abs(math.sin(t * 7)), look=(-1, 0))
        return p
    def back(fr, c):
        lamp_cone(fr, c)
    def front(fr, c):
        table(fr, c, c["gy"] - 330)
        big_text(fr, 300, c["gy"] - 1080, "?", 160, eob((lt - 0.4) / 0.3), ang=-10)
    return dict(hero=hero, hx=330, extras=[dict(x=820, style=OFFICER, posefn=officer)], back=back, front=front)


def A_silent(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(70, -430), rh=(-70, -415), shades=1, mouth="flat", look=(0, 0))
        return p
    def officer(t, talk):
        p = default_pose(t, 0, 2)
        p.update(lh=(-180, -560), rh=(180, -560), lh_shape="open", rh_shape="open", brows="up", mouth="o", look=(-1, 0))
        return p
    def front(fr, c):
        table(fr, c, c["gy"] - 330)
        d = ImageDraw.Draw(fr)
        k = eob((lt - 0.3) / 0.3)
        C.bubble(d, 160, c["gy"] - 1000, k, 220, 120, col=(255, 255, 255))
        if k > 0.5:
            for i in range(3):
                x = 160 + 220 * k * (0.3 + i * 0.2)
                d.ellipse([x - 12, c["gy"] - 1000 + 48 * k, x + 12, c["gy"] - 1000 + 72 * k], fill=INK)
    return dict(hero=hero, hx=330, extras=[dict(x=820, style=OFFICER, posefn=officer)], back=lambda fr, c: lamp_cone(fr, c), front=front)


def A_spot(c):
    lt = c["lt"]
    def beam_x():
        return 540 + 420 * math.sin(c["t"] * 1.6)
    def hero(t, talk):
        p = default_pose(t, talk)
        lit = abs(beam_x() - 400) < 170
        p.update(lh=(-120, -330), rh=(120, -330), look=(1, -0.5), brows="up" if lit else "angry", mouth="o" if lit else "flat")
        return p
    def front(fr, c):
        searchlight(fr, c, beam_x())
        if abs(beam_x() - 400) < 170:
            big_text(fr, 400, c["gy"] - 1060, "!", 200, 1.0, col=(255, 90, 110))
    return dict(hero=hero, hx=400, front=front)


def A_dig(c):
    """Il creuse sous la couchette avec une cuillere (le plan)."""
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        dg = math.sin(t * 10)
        p.update(rh=(200 + 30 * dg, -260 + 40 * dg), rh_shape="fist", look=(1, 1), brows="angry", mouth="smirk")
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        hole = 60 + 90 * clamp(lt / 1.5)
        d.ellipse([700 - hole, c["gy"] - 40, 700 + hole, c["gy"] + 30], fill=(20, 18, 24), outline=INK, width=6)
        rnd = random.Random(int(c["t"] * 8))
        for _ in range(5):  # cailloux qui volent
            x, y = 700 + rnd.randint(-120, 120), c["gy"] - rnd.randint(60, 260)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(120, 110, 100), outline=INK, width=3)
    return dict(hero=hero, hx=480, front=front)


def A_run(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t * 1.8, talk)
        sw = math.sin(t * 16)
        p.update(walk=1.4, lh=(-170 + 90 * sw, -380), rh=(170 - 90 * sw, -380), look=(1, 0), brows="angry", mouth="o", bob=8 * abs(sw))
        return p
    hx = -100 + 1050 * ease(lt / 2.3)
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(6):  # traits de vitesse
            y = c["gy"] - 200 - i * 110
            d.line([hx - 380 - i * 30, y, hx - 180, y], fill=(255, 255, 255), width=6)
        searchlight(fr, c, hx - 250 - 120 * math.sin(c["t"] * 3))
    return dict(hero=hero, hx=hx, front=front)


def A_free(c):
    lt = c["lt"]
    op = ease(lt / 0.9)
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        gx0, gx1, gy0 = 260, 820, 700
        glow(fr, 540, 1150, 380 * op + 10, (255, 236, 180), int(200 * op))
        d = ImageDraw.Draw(fr)
        d.rectangle([gx0 + 280 * (1 - op), gy0, gx1 - 280 * (1 - op), c["gy"]], fill=(255, 246, 214))
        d.rectangle([gx0 - 40, gy0 - 40, gx1 + 40, gy0], fill=(80, 84, 100), outline=INK, width=LW)
        for side in (-1, 1):  # deux battants qui s'ecartent
            w = 280
            x0 = (gx0 - w * op) if side == -1 else (540 + w * op)
            d.rectangle([x0, gy0, x0 + w, c["gy"]], fill=(70, 74, 90), outline=INK, width=LW)
            for x in range(int(x0) + 30, int(x0) + w, 50):
                d.line([x, gy0, x, c["gy"]], fill=(40, 42, 54), width=10)
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(walk=1 if lt > 0.6 else 0, lh=(-110, -330), rh=(110, -330), shades=ease((lt - 1.0) / 0.4), mouth="smile" if talk < 0.25 else "talk")
        return p
    return dict(hero=hero, hx=540, hero_s=1.0 - 0.25 * ease((lt - 0.6) / 1.4), back=back)


C.ACTIONS.update(count=A_count, grip=A_grip, interro=A_interro, silent=A_silent, spot=A_spot, dig=A_dig,
                 run=A_run, free=A_free)

if __name__ == "__main__":
    C.main()
