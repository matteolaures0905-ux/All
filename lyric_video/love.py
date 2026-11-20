#!/usr/bin/env python3
"""Extension "histoire d'amour nocturne" pour cartoon2.py (2e son).

  python3 love.py --lyrics son2_amour.json --audio son2_brut.m4a --duration 31.5 --hero dark --night --out video.mp4
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import cartoon2 as C
import prison  # noqa: F401  (decors/actions supplementaires)
from cartoon2 import W, H, INK, ACC, LW, ease, eob, clamp, shade, glow, default_pose, big_text, burst, bubble, paste, bill_img, font

GIRL = dict(skin=(214, 158, 118), skin_d=(184, 126, 90), jacket=(232, 90, 140), jacket_d=(196, 64, 112),
            sleeve=(232, 90, 140), sleeve_d=(196, 64, 112), cuff=(250, 220, 235), pants=(40, 36, 60),
            shoe=(250, 250, 250), sole=(230, 200, 220), shoe_acc=(232, 90, 140), hat="long",
            hat_col=(40, 26, 20), hair=(46, 30, 24), chain=False, patch=False, tee=(250, 240, 245),
            earrings=True, lashes=True)
PINK = (255, 90, 150)


def draw_tank(fr, x, y, s=1.0):
    """Bonbonne de gaz metallique avec un gros noeud rose (offerte comme une dot)."""
    d = ImageDraw.Draw(fr)
    w, h = 90 * s, 300 * s
    d.rounded_rectangle([x - w, y - h / 2, x + w, y + h / 2], int(70 * s), fill=(190, 196, 214), outline=INK, width=7)
    d.rounded_rectangle([x - w + 18 * s, y - h / 2 + 30 * s, x - w + 40 * s, y + h / 2 - 30 * s], int(10 * s), fill=(240, 244, 255))
    d.rounded_rectangle([x + w - 34 * s, y - h / 2 + 30 * s, x + w - 14 * s, y + h / 2 - 30 * s], int(10 * s), fill=(150, 156, 176))
    d.chord([x - w, y - h / 2 - 2, x + w, y - h / 2 + 120 * s], 180, 360, fill=(60, 120, 230), outline=INK, width=7)
    d.rectangle([x - 26 * s, y - h / 2 - 70 * s, x + 26 * s, y - h / 2 + 4], fill=(150, 156, 176), outline=INK, width=6)
    d.rounded_rectangle([x - 50 * s, y - h / 2 - 96 * s, x + 50 * s, y - h / 2 - 66 * s], int(10 * s), fill=(60, 120, 230), outline=INK, width=6)
    d.rectangle([x - w + 6, y - 40 * s, x + w - 6, y + 40 * s], fill=(255, 255, 255), outline=INK, width=5)
    d.text((x, y), "AZOTE", font=font(int(46 * s)), fill=INK, anchor="mm")
    for sx in (-1, 1):  # noeud rose
        d.ellipse([x + sx * 70 * s - 48 * s, y - h / 2 + 10 * s, x + sx * 70 * s + 48 * s, y - h / 2 + 80 * s], fill=PINK, outline=INK, width=5)
    d.ellipse([x - 22 * s, y - h / 2 + 24 * s, x + 22 * s, y - h / 2 + 66 * s], fill=(255, 140, 190), outline=INK, width=5)


def heart(d, x, y, r, col=PINK, outline=True):
    if r < 12:  # trop petit pour etre dessine (debut d'animation)
        return
    d.ellipse([x - r, y - r, x, y], fill=col, outline=INK if outline else None, width=4)
    d.ellipse([x, y - r, x + r, y], fill=col, outline=INK if outline else None, width=4)
    d.polygon([(x - r + 2, y - r * 0.4), (x + r - 2, y - r * 0.4), (x, y + r)], fill=col, outline=INK if outline else None)
    d.ellipse([x - r + 5, y - r + 5, x - 5, y - 5], fill=col)
    d.ellipse([x + 5, y - r + 5, x + r - 5, y - 5], fill=col)
    d.ellipse([x - r * 0.75, y - r * 0.8, x - r * 0.45, y - r * 0.5], fill=(255, 210, 230))


def hearts_rise(fr, c, x0, y0, n=8, seed=1):
    d = ImageDraw.Draw(fr)
    rnd = random.Random(seed)
    for i in range(n):
        ph = (c["lt"] * 0.7 + i / n) % 1
        x = x0 + rnd.randint(-260, 260) + 30 * math.sin(c["t"] * 3 + i)
        y = y0 - 600 * ph
        heart(d, x, y, 22 + 26 * (1 - ph))


def devil(fr, x, y, s, t, point=None):
    d = ImageDraw.Draw(fr)
    red, dark = (220, 40, 60), (160, 20, 40)
    b = 8 * math.sin(t * 5)
    y += b
    # queue
    d.line([(x + 40 * s, y + 80 * s), (x + 120 * s, y + 120 * s), (x + 150 * s, y + 60 * s)], fill=INK, width=int(14 * s))
    d.line([(x + 40 * s, y + 80 * s), (x + 120 * s, y + 120 * s), (x + 150 * s, y + 60 * s)], fill=red, width=int(8 * s))
    d.polygon([(x + 150 * s, y + 30 * s), (x + 175 * s, y + 70 * s), (x + 130 * s, y + 70 * s)], fill=red, outline=INK)
    # ailes de chauve-souris
    for k in (-1, 1):
        d.polygon([(x + 50 * k * s, y), (x + 170 * k * s, y - 70 * s), (x + 150 * k * s, y + 10 * s), (x + 120 * k * s, y - 10 * s), (x + 100 * k * s, y + 40 * s)], fill=dark, outline=INK)
    d.ellipse([x - 80 * s, y - 80 * s, x + 80 * s, y + 90 * s], fill=red, outline=INK, width=6)
    for k in (-1, 1):  # cornes
        d.polygon([(x + 30 * k * s, y - 70 * s), (x + 70 * k * s, y - 140 * s), (x + 55 * k * s, y - 60 * s)], fill=(250, 240, 220), outline=INK)
        d.polygon([(x + 22 * k * s - 9 * s, y - 20 * s), (x + 22 * k * s + 9 * s, y - 20 * s), (x + 22 * k * s, y + 4 * s)], fill=(255, 220, 60), outline=INK)
    d.chord([x - 40 * s, y + 10 * s, x + 40 * s, y + 60 * s], 0, 180, fill=INK)
    for k in (-1, 1):
        d.polygon([(x + 20 * k * s - 8 * s, y + 35 * s), (x + 20 * k * s + 8 * s, y + 35 * s), (x + 20 * k * s, y + 50 * s)], fill=(255, 255, 255))
    if point:
        d.line([(x - 70 * s, y + 20 * s), point], fill=INK, width=int(18 * s))
        d.line([(x - 70 * s, y + 20 * s), point], fill=red, width=int(10 * s))


def calendar(fr, x, y, k, circled):
    d = ImageDraw.Draw(fr)
    w, h = 300 * k, 330 * k
    if k < 0.05:
        return
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], int(20 * k), fill=(250, 248, 240), outline=INK, width=6)
    d.rectangle([x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 70 * k], fill=(220, 40, 60), outline=INK, width=6)
    for r in range(4):
        for cc in range(5):
            cx_, cy_ = x - w / 2 + (30 + cc * 60) * k, y - h / 2 + (100 + r * 55) * k
            d.rectangle([cx_, cy_, cx_ + 40 * k, cy_ + 36 * k], fill=(220, 220, 228))
    if circled > 0:
        cx_, cy_ = x - w / 2 + (30 + 3 * 60 + 20) * k, y - h / 2 + (100 + 2 * 55 + 18) * k
        d.arc([cx_ - 46 * k, cy_ - 40 * k, cx_ + 46 * k, cy_ + 40 * k], 0, 360 * circled, fill=(220, 40, 60), width=int(10 * k))


def supercar(fr, x, y, s=1.0, glow_on=True):
    """Voiture de sport orange en coin (design original)."""
    d = ImageDraw.Draw(fr)
    org, dk = (255, 130, 30), (200, 90, 10)
    if glow_on:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(x + 400 * s, y - 70 * s), (W + 300, y - 260 * s), (W + 300, y + 120 * s)], fill=(255, 250, 200, 70))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
        d = ImageDraw.Draw(fr)
    body = [(x - 430 * s, y - 40 * s), (x - 380 * s, y - 110 * s), (x - 140 * s, y - 150 * s), (x + 40 * s, y - 210 * s),
            (x + 200 * s, y - 200 * s), (x + 430 * s, y - 90 * s), (x + 440 * s, y - 20 * s), (x - 420 * s, y + 10 * s)]
    d.polygon(body, fill=org, outline=INK)
    d.line(body + [body[0]], fill=INK, width=8)
    d.polygon([(x - 90 * s, y - 150 * s), (x + 50 * s, y - 196 * s), (x + 190 * s, y - 188 * s), (x + 260 * s, y - 140 * s)], fill=(30, 34, 50), outline=INK)
    d.line([(x + 60 * s, y - 192 * s), (x + 40 * s, y - 145 * s)], fill=INK, width=6)
    d.line([(x - 300 * s, y - 90 * s), (x + 380 * s, y - 70 * s)], fill=dk, width=int(10 * s))  # arete
    for k in range(3):  # prises d'air
        d.polygon([(x + 120 * s + k * 26 * s, y - 120 * s), (x + 140 * s + k * 26 * s, y - 120 * s), (x + 130 * s + k * 26 * s, y - 60 * s), (x + 110 * s + k * 26 * s, y - 60 * s)], fill=INK)
    d.polygon([(x + 380 * s, y - 85 * s), (x + 432 * s, y - 70 * s), (x + 425 * s, y - 50 * s), (x + 370 * s, y - 62 * s)], fill=(255, 250, 210), outline=INK)
    d.polygon([(x - 420 * s, y - 50 * s), (x - 380 * s, y - 70 * s), (x - 385 * s, y - 45 * s)], fill=(255, 40, 60), outline=INK)
    for wx in (x - 250 * s, x + 260 * s):  # roues
        d.ellipse([wx - 85 * s, y - 70 * s, wx + 85 * s, y + 100 * s], fill=INK)
        d.ellipse([wx - 55 * s, y - 40 * s, wx + 55 * s, y + 70 * s], fill=(180, 184, 200), outline=INK, width=5)
        for a in range(0, 360, 72):
            r = math.radians(a)
            d.line([wx, y + 15 * s, wx + 50 * s * math.cos(r), y + 15 * s + 50 * s * math.sin(r)], fill=(90, 94, 110), width=int(8 * s))
        d.ellipse([wx - 14 * s, y + 1 * s, wx + 14 * s, y + 29 * s], fill=ACC, outline=INK, width=3)


def scale_balance(fr, c, tilt):
    d = ImageDraw.Draw(fr)
    cx, cy = 720, c["gy"] - 720
    d.rectangle([cx - 14, cy, cx + 14, c["gy"] - 200], fill=(200, 170, 80), outline=INK, width=5)
    d.polygon([(cx - 120, c["gy"] - 200), (cx + 120, c["gy"] - 200), (cx + 80, c["gy"] - 250), (cx - 80, c["gy"] - 250)], fill=(200, 170, 80), outline=INK)
    a = math.radians(-14 * tilt)
    L = 230
    lx, ly = cx - L * math.cos(a), cy - L * math.sin(a)
    rx, ry = cx + L * math.cos(a), cy + L * math.sin(a)
    d.line([lx, ly, rx, ry], fill=INK, width=16); d.line([lx, ly, rx, ry], fill=(230, 200, 100), width=8)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=ACC, outline=INK, width=5)
    for (px, py, cash) in ((lx, ly, False), (rx, ry, True)):
        d.line([px, py, px - 70, py + 140], fill=INK, width=4); d.line([px, py, px + 70, py + 140], fill=INK, width=4)
        d.chord([px - 100, py + 100, px + 100, py + 180], 0, 180, fill=(230, 200, 100), outline=INK, width=6)
        if cash:
            for k in range(4):
                d.rounded_rectangle([px - 70, py + 112 - k * 24, px + 70, py + 136 - k * 24], 6, fill=(150, 210, 140), outline=INK, width=4)
                d.ellipse([px - 12, py + 116 - k * 24, px + 12, py + 132 - k * 24], fill=(90, 160, 90))
        else:
            big_text(fr, px, py + 90, "?", 90, 1.0, col=(255, 255, 255))
            d = ImageDraw.Draw(fr)


def phone_glow(fr, C_, s, t):
    C.prop_phone(fr, C_, s, t)
    glow(fr, C_[0], C_[1] - 60 * s, 60, (110, 230, 200), 90)


# ====================================================================== actions
def girl_pose(kind, lt):
    def f(t, talk):
        p = default_pose(t, 0, 1.3)
        p["talk"] = 0
        if kind == "doubt":
            p.update(lh=(70, -430), rh=(-70, -415), brows="skeptic", mouth="flat", look=(-1, 0))
        elif kind == "phone":
            p.update(rh=(140, -700), rh_prop=phone_glow, brows="angry", mouth="talk", talk=0.35 + 0.3 * abs(math.sin(t * 8)), look=(1, 0))
        elif kind == "spell":
            p.update(lh=(-230, -640 + 40 * math.sin(t * 4)), rh=(230, -640 + 40 * math.cos(t * 4)), lh_shape="open", rh_shape="open",
                     eyes="closed", mouth="smile", bob=10 * math.sin(t * 3))
        elif kind == "love":
            p.update(lh=(-60, -560), rh=(60, -560), mouth="smile", eyes="closed", look=(-1, 0))
        elif kind == "angry":
            g = math.sin(t * 10)
            p.update(rh=(200 + 40 * g, -680), rh_shape="point", lh=(-150, -330), brows="angry", mouth="talk", talk=0.5 + 0.3 * abs(g), look=(-1, 0))
        elif kind == "kiss":
            p.update(lh=(-200, -560), lh_shape="open", mouth="o", eyes="closed", look=(-1, 0))
        elif kind == "wow":
            p.update(lh=(-60, -640), rh=(60, -640), lh_shape="open", rh_shape="open", mouth="smile", brows="up", look=(-1, 0))
        else:
            p.update(mouth="smile", look=(-1, 0))
        return p
    return f


def A_gift(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        k = ease(lt / 0.6)
        p.update(rh=(150 + 120 * k, -420), rh_shape="open", look=(1, 0), mouth="smirk")
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = ease(lt / 0.6)
        x, y = c["hx"] + 150 + 120 * k + 60, c["gy"] - 560
        draw_tank(fr, x, y)
        big_text(fr, x, y - 230, "?!", 110, eob((lt - 0.5) / 0.3), ang=8)
    return dict(hero=hero, hx=280, extras=[dict(x=800, style=GIRL, posefn=girl_pose("wow", lt), s=0.86)], front=front)


def A_devil(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(look=(1, -1), brows="up", mouth="o" if talk < 0.25 else "talk")
        return p
    def front(fr, c):
        calendar(fr, 700, 780, eob(lt / 0.3), clamp((lt - 0.4) / 0.6))
        devil(fr, 860 + 20 * math.sin(c["t"] * 2), 520, 0.9, c["t"], point=(790, 820))
    return dict(hero=hero, hx=260, front=front)


def A_doubt(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(-90, -330), rh=(40, -470), rh_shape="point", mouth="smirk" if talk < 0.25 else "talk", look=(1, 0), brows="neutral")
        return p
    def front(fr, c):
        big_text(fr, 800, c["gy"] - 1060, "?", 170, eob((lt - 0.2) / 0.3), ang=-10)
    return dict(hero=hero, hx=300, extras=[dict(x=800, style=GIRL, posefn=girl_pose("doubt", lt), s=0.86)], front=front)


def A_scale(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        drop = ease((lt - 0.3) / 0.3)
        p.update(rh=(250, -560 + 80 * drop), rh_shape="open", shades=1, mouth="smirk", look=(1, 0))
        return p
    def front(fr, c):
        scale_balance(fr, c, ease((lt - 0.4) / 0.5) * 2 - 1)
    return dict(hero=hero, hx=280, front=front)


def A_call5(c):
    lt = c["lt"]
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        x, y = 760, 640
        d.rounded_rectangle([x - 170, y - 70, x + 170, y + 70], 20, fill=(20, 18, 26), outline=INK, width=8)
        on = (c["t"] * 2) % 1 < 0.7
        d.text((x, y), "05:00", font=font(110), fill=(255, 60, 70) if on else (90, 30, 34), anchor="mm")
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(3):
            r = 120 + i * 40 + 30 * ((c["t"] * 2) % 1)
            x, y = 640, c["gy"] - 800
            d.arc([x - r, y - r, x + r, y + r], -50, 50, fill=(110, 230, 200), width=7)
    return dict(hero=None, extras=[dict(x=480, style=GIRL, posefn=girl_pose("phone", lt), s=0.95)], back=back, front=front)


def A_spell(c):
    lt = c["lt"]
    def front(fr, c):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        cx, cy = 540, c["gy"] - 520
        for i in range(14):  # tourbillon magique
            a = c["t"] * 2.5 + i * math.tau / 14
            r = 260 + 40 * math.sin(c["t"] * 3 + i)
            x, y = cx + r * math.cos(a), cy + r * 0.55 * math.sin(a)
            col = [(190, 120, 255), (255, 120, 220), (120, 220, 255)][i % 3]
            ld.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col + (230,))
        for i in range(3):  # fumee violette
            ph = (lt * 0.6 + i / 3) % 1
            ld.ellipse([cx - 120 + i * 80, c["gy"] - 200 - 500 * ph, cx + 20 + i * 80, c["gy"] - 80 - 500 * ph], fill=(160, 90, 220, int(120 * (1 - ph))))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
        d = ImageDraw.Draw(fr)
        for i in range(6):  # etincelles
            a = c["t"] * 4 + i
            x, y = cx + 330 * math.cos(a), cy - 300 + 120 * math.sin(a * 1.3)
            d.line([x - 18, y, x + 18, y], fill=(255, 240, 160), width=6); d.line([x, y - 18, x, y + 18], fill=(255, 240, 160), width=6)
        # yeux en spirale par-dessus ses yeux fermes
        for k in (-1, 1):
            ex, ey = 540 + 40 * k * 0.92, c["gy"] - 695 * 0.92 + 10 * math.sin(c["t"] * 3) * 0.92
            for j in range(3):
                r = 6 + j * 8
                d.arc([ex - r, ey - r, ex + r, ey + r], int(c["t"] * 300 + j * 120) % 360, int(c["t"] * 300 + j * 120 + 240) % 360, fill=(190, 120, 255), width=5)
    return dict(hero=None, extras=[dict(x=540, style=GIRL, posefn=girl_pose("spell", lt), s=0.92)], front=front)


def A_rush(c):
    lt = c["lt"]
    hx = -120 + 700 * ease(lt / 1.6)
    def hero(t, talk):
        p = default_pose(t * 1.8, talk)
        sw = math.sin(t * 16)
        p.update(walk=1.4 if lt < 1.6 else 0, lh=(-170 + 90 * sw, -380), rh=(170 - 90 * sw, -380), look=(1, 0), mouth="smirk", bob=8 * abs(sw))
        return p
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        x0 = 700  # porte de l'immeuble d'elle, eclairee
        glow(fr, x0 + 140, c["gy"] - 420, 220, (255, 220, 150), 120)
        d = ImageDraw.Draw(fr)
        d.rectangle([x0, c["gy"] - 700, x0 + 280, c["gy"]], fill=(60, 40, 70), outline=INK, width=LW)
        d.rectangle([x0 + 30, c["gy"] - 660, x0 + 250, c["gy"]], fill=(255, 220, 160), outline=INK, width=6)
        heart(d, x0 + 140, c["gy"] - 760, 40)
        for i in range(5):
            y = c["gy"] - 220 - i * 100
            d.line([hx - 360 - i * 25, y, hx - 170, y], fill=(255, 255, 255), width=6)
    return dict(hero=hero, hx=hx, back=back)


def A_hearts(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(rh=(230, -560), mouth="smile" if talk < 0.25 else "talk", look=(1, 0))
        return p
    def front(fr, c):
        hearts_rise(fr, c, 540, c["gy"] - 500, 10)
        d = ImageDraw.Draw(fr)
        k = eob((lt - 0.2) / 0.3) * (1 + 0.08 * math.sin(c["t"] * 10))
        heart(d, 540, c["gy"] - 1020, 110 * k)
    return dict(hero=hero, hx=360, extras=[dict(x=700, style=GIRL, posefn=girl_pose("love", lt), s=0.86)], front=front)


def A_zip(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        z = ease(lt / 0.8)
        p.update(rh=(10, -280 - 330 * z), rh_shape="fist", hood=lt > 0.9, brows="angry", mouth="flat" if talk < 0.25 else "talk",
                 walk=1 if lt > 1.0 else 0)
        return p
    hx = 540 + 500 * ease((lt - 1.0) / 1.2)
    return dict(hero=hero, hx=hx, front=lambda fr, c: C.rain(fr, c["t"]) if lt > 0.9 else None)


def A_think(c, phone=False):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        if phone:
            p.update(rh=(60, -560), rh_prop=phone_glow, look=(0.5, 1), mouth="smirk")
        else:
            p.update(lh=(70, -430), rh=(-70, -415), look=(1, -1), mouth="smirk" if talk < 0.25 else "talk")
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = eob((lt - 0.2) / 0.35)
        x, y = c["hx"] + 280, c["gy"] - 1080
        for i, r in enumerate((14, 22, 32)):  # petites bulles de pensee
            d.ellipse([c["hx"] + 90 + i * 55 - r, c["gy"] - 830 - i * 60 - r, c["hx"] + 90 + i * 55 + r, c["gy"] - 830 - i * 60 + r], fill=(255, 255, 255), outline=INK, width=4)
        if k > 0.05:
            d.ellipse([x - 190 * k, y - 140 * k, x + 190 * k, y + 140 * k], fill=(255, 255, 255), outline=INK, width=6)
            gp = girl_pose("love", lt)(c["t"], 0)
            sub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            C.draw_person(sub, x, y + 330 * k, c["t"], GIRL, gp, s=0.42 * k)
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).ellipse([x - 180 * k, y - 130 * k, x + 180 * k, y + 130 * k], fill=255)
            fr.paste(sub, (0, 0), Image.composite(sub.getchannel("A"), Image.new("L", (W, H), 0), m))
            d = ImageDraw.Draw(fr)
            heart(d, x + 150 * k, y - 100 * k, 34 * k)
    return dict(hero=hero, hx=330, front=front)


def draw_reaper(fr, x, y, s, t):
    """Faucheuse originale : grande robe a capuche dechiree, crane, yeux rouges, faux."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    sway = 14 * math.sin(t * 2)
    robe = [(x - 90 * s, y - 520 * s), (x + 90 * s, y - 520 * s), (x + 230 * s + sway, y)]
    for i in range(7):  # bas dechire
        xx = x + 230 * s - i * (460 * s / 6) + sway
        robe.append((xx, y + (40 if i % 2 else -10) * s))
    robe.append((x - 230 * s + sway, y))
    d.polygon(robe, fill=(14, 12, 22, 235), outline=INK + (255,))
    d.ellipse([x - 120 * s, y - 700 * s, x + 120 * s, y - 440 * s], fill=(14, 12, 22, 245), outline=INK + (255,), width=6)
    d.ellipse([x - 75 * s, y - 640 * s, x + 75 * s, y - 480 * s], fill=(4, 4, 8, 255))
    d.ellipse([x - 55 * s, y - 630 * s, x + 55 * s, y - 520 * s], fill=(226, 220, 204, 255), outline=INK + (255,), width=4)
    d.rectangle([x - 30 * s, y - 530 * s, x + 30 * s, y - 495 * s], fill=(226, 220, 204, 255), outline=INK + (255,), width=3)
    for k in range(-2, 3):
        d.line([x + k * 11 * s, y - 530 * s, x + k * 11 * s, y - 497 * s], fill=INK + (255,), width=3)
    for k in (-1, 1):
        d.ellipse([x + k * 24 * s - 16 * s, y - 600 * s, x + k * 24 * s + 16 * s, y - 566 * s], fill=(10, 0, 0, 255))
        d.ellipse([x + k * 24 * s - 7 * s, y - 590 * s, x + k * 24 * s + 7 * s, y - 576 * s], fill=(255, 40, 50, 255))
    d.polygon([(x - 6 * s, y - 560 * s), (x + 6 * s, y - 560 * s), (x, y - 545 * s)], fill=INK + (255,))
    # faux
    d.line([x + 170 * s, y - 900 * s, x + 120 * s, y - 40 * s], fill=INK + (255,), width=int(22 * s))
    d.line([x + 170 * s, y - 900 * s, x + 120 * s, y - 40 * s], fill=(110, 76, 50, 255), width=int(12 * s))
    blade = [(x + 172 * s, y - 900 * s), (x - 140 * s, y - 960 * s), (x - 300 * s, y - 860 * s), (x - 80 * s, y - 900 * s), (x + 165 * s, y - 860 * s)]
    d.polygon(blade, fill=(200, 206, 222, 255), outline=INK + (255,))
    d.line([(x - 280 * s, y - 866 * s), (x - 120 * s, y - 930 * s)], fill=(255, 255, 255, 255), width=5)
    glow_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow_l).ellipse([x - 70 * s, y - 640 * s, x + 70 * s, y - 540 * s], fill=(255, 30, 40, int(90 + 80 * C.VOC[0])))
    fr.alpha_composite(glow_l.filter(ImageFilter.GaussianBlur(20)))
    fr.alpha_composite(lay)


def skull_box(d, x, y, k=1.0):
    d.rounded_rectangle([x - 50 * k, y - 36 * k, x + 50 * k, y + 36 * k], int(8 * k), fill=(20, 18, 26), outline=INK, width=5)
    d.ellipse([x - 20 * k, y - 26 * k, x + 20 * k, y + 8 * k], fill=(236, 230, 214))
    d.rectangle([x - 11 * k, y + 4 * k, x + 11 * k, y + 18 * k], fill=(236, 230, 214))
    for e in (-1, 1):
        d.ellipse([x + e * 9 * k - 6 * k, y - 14 * k, x + e * 9 * k + 6 * k, y - 2 * k], fill=INK)


def A_reaper(c):
    lt = c["lt"]
    give = ease((lt - 0.3) / 0.5)
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(-160 - 120 * give, -420), lh_shape="open", look=(-1, 0), brows="angry", mouth="flat" if talk < 0.25 else "talk", hood=True)
        return p
    def back(fr, c):
        fr.alpha_composite(Image.new("RGBA", (W, H), (20, 0, 10, 90)))
        draw_reaper(fr, 800, c["gy"] - 10, 1.18, c["t"])
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        hx_, hy_ = c["hx"] - 0.92 * (160 + 120 * give), c["gy"] - 0.92 * 420
        skull_box(d, hx_ - 50, hy_ - 60, 1.7)
        reach = ease((lt - 0.2) / 0.6)
        for i, yy in enumerate((hy_ - 140, hy_ + 40)):  # mains d'ombre qui sortent du noir
            x1 = -40 + (hx_ - 120) * reach * (0.85 + 0.1 * i)
            for col, wd, fw in (((170, 90, 255), 58, 20), ((10, 6, 18), 44, 11)):
                d.line([(-60, yy + 60), (x1, yy)], fill=col, width=wd)
                for f in range(4):
                    d.line([(x1, yy), (x1 + 46, yy - 34 + f * 22)], fill=col, width=fw)
        # il pense a elle : bulle de pensee
        A_think(c)["front"](fr, c)
    return dict(hero=hero, hx=420, back=back, front=front)


def A_argue(c):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(rh=(80, -760), rh_shape="open", lh=(-150, -330), eyes="closed", brows="angry", mouth="frown", look=(1, 0))
        return p
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        rnd = random.Random(int(c["t"] * 10))
        for i in range(3):  # bulles de dispute gribouillees
            k = eob((lt - 0.1 - i * 0.25) / 0.25)
            if k < 0.05:
                continue
            x, y = 560 + i * 120, c["gy"] - 1080 + i * 90
            d.rounded_rectangle([x, y, x + 200 * k, y + 110 * k], int(30 * k), fill=(255, 80, 90), outline=INK, width=6)
            pts = [(x + 25 * k + j * 18 * k, y + 55 * k + rnd.randint(-28, 28) * k) for j in range(9)]
            d.line(pts, fill=INK, width=6)
        for i in range(4):  # eclairs de colere au-dessus de lui
            a = c["t"] * 3 + i * 1.6
            x, y = c["hx"] + 130 * math.cos(a), c["gy"] - 900 + 30 * math.sin(a)
            d.line([(x, y), (x + 14, y + 26), (x - 6, y + 30), (x + 10, y + 58)], fill=ACC, width=7)
    return dict(hero=hero, hx=300, extras=[dict(x=800, style=GIRL, posefn=girl_pose("angry", lt), s=0.86)], front=front)


def A_car(c, kiss=False):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        p.update(lh=(-90, -330), rh=(250, -520) if not kiss else (200, -420), rh_shape="open", shades=1, mouth="smile" if kiss else "smirk", look=(1, 0))
        return p
    def back(fr, c):
        supercar(fr, 600, c["gy"] - 330, 0.9)
    def front(fr, c):
        if kiss:
            hearts_rise(fr, c, 440, c["gy"] - 600, 6, seed=3)
            d = ImageDraw.Draw(fr)
            k = eob((lt - 0.4) / 0.3)
            heart(d, 360, c["gy"] - 960, 50 * k)
        else:
            d = ImageDraw.Draw(fr)
            for i in range(4):
                a = c["t"] * 2 + i * 1.57
                x, y = 560 + 420 * math.cos(a), c["gy"] - 300 + 60 * math.sin(a)
                d.line([x - 16, y, x + 16, y], fill=(255, 250, 220), width=6); d.line([x, y - 16, x, y + 16], fill=(255, 250, 220), width=6)
    extras = [dict(x=480 if kiss else 760, style=GIRL, posefn=girl_pose("kiss" if kiss else "wow", lt), s=0.86)]
    return dict(hero=hero, hx=300 if kiss else 260, extras=extras, back=back, front=front)


def A_cash(c, rain=False):
    lt = c["lt"]
    def hero(t, talk):
        p = default_pose(t, talk)
        if rain:
            sw = math.sin(t * 9)
            p.update(rh=(200 + 50 * sw, -760), rh_shape="open", lh=(-200, -700), lh_shape="open", shades=1, mouth="smile")
        else:
            k = ease(lt / 0.5)
            p.update(rh=(110 + 150 * k, -330 - 300 * k), rh_shape="fist", look=(1, -0.5), mouth="smirk")
        return p
    def front(fr, c):
        b = bill_img()
        if rain:
            rnd = random.Random(21)
            for i in range(18):
                ph = (lt * 0.8 + i / 18) % 1
                x = rnd.randint(0, W) + 60 * math.sin(c["t"] * 2 + i)
                y = -100 + 1500 * ph
                paste(fr, b, x, y, ang=(c["t"] * 120 + i * 37) % 360, k=0.4)
        else:
            k = ease(lt / 0.5)
            x, y = c["hx"] + 110 + 150 * k, c["gy"] - 0.92 * (330 + 300 * k) - 40
            for i in range(5):  # eventail de billets
                paste(fr, b, x + (i - 2) * 22, y - 50, ang=(i - 2) * 16, k=0.45 * k + 0.01)
            d = ImageDraw.Draw(fr)
            d.text((x, y - 210), "10K", font=font(int(90 * k) + 1), fill=(150, 230, 140), anchor="mm", stroke_width=6, stroke_fill=INK)
    girl = dict(x=800, style=GIRL, posefn=girl_pose("love" if rain else "wow", lt), s=0.86)
    def front2(fr, c):
        front(fr, c)
        if rain:
            hearts_rise(fr, c, 800, c["gy"] - 700, 6, seed=9)
    return dict(hero=hero, hx=300, extras=[girl], front=front2)


C.ACTIONS.update(reaper=A_reaper, gift=A_gift, devil=A_devil, doubt=A_doubt, scale=A_scale, call5=A_call5, spell=A_spell, rush=A_rush,
                 hearts=A_hearts, zip=A_zip, think=A_think, think_phone=lambda c: A_think(c, phone=True), argue=A_argue,
                 car=A_car, car_kiss=lambda c: A_car(c, kiss=True), cash=A_cash, cash_rain=lambda c: A_cash(c, rain=True))

if __name__ == "__main__":
    C.main()
