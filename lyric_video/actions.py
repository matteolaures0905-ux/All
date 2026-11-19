"""Mises en scene par ligne : chaque "action" illustre le sens d'une phrase.

Une action = dict avec :
  extras  : nombre de figurants
  hero_x  : fonction(lt) -> position x du heros (None = pas de heros)
  pose    : "idle" | "shrug" | "phone" | "think" | "look"
  back    : fonction(frame, c) dessinee AVANT les personnages
  front   : fonction(frame, c) dessinee APRES les personnages
c = contexte : t, lt (temps depuis le debut de la ligne), dur (duree ligne), gy (sol), p (kick), hx
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
INK = (22, 22, 24)
ACC = (247, 176, 49)
ACC_D = (196, 128, 20)
G = [(30, 30, 32), (58, 58, 60), (88, 88, 90), (120, 120, 122), (152, 152, 154),
     (184, 184, 186), (214, 214, 216), (238, 238, 240)]
FONT = None  # injecte par make_cartoon


def eob(x):
    x = min(max(x, 0), 1)
    return 1 + 3.2 * (x - 1) ** 3 + 2.2 * (x - 1) ** 2


def ease(x):
    x = min(max(x, 0), 1)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ accessoires
def bubble(d, x, y, k, w=240, h=130, dark=True, lines=3, face=False):
    if k <= 0.02:
        return
    w, h = w * k, h * k
    fill, ln = (G[0], G[7]) if dark else (G[7], G[0])
    d.polygon([(x + w * 0.2, y + h - 4), (x + w * 0.1, y + h + 36 * k), (x + w * 0.38, y + h - 4)], fill=fill, outline=INK)
    d.rounded_rectangle([x, y, x + w, y + h], int(36 * k) + 1, fill=fill, outline=INK, width=6)
    if face:  # mini-tete du heros dans la bulle
        cx, cy, r = x + w / 2, y + h / 2 + 6 * k, 34 * k
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=G[6], outline=INK, width=4)
        d.chord([cx - r, cy - r - 8 * k, cx + r, cy + r * 0.4], 180, 360, fill=ACC, outline=INK, width=4)
        return
    for i in range(lines):
        yy = y + (h / (lines + 1)) * (i + 1)
        d.line([x + 30 * k, yy, x + w - (30 + 40 * (i % 2)) * k, yy], fill=ln, width=max(1, int(12 * k)))


def qmark(frame, x, y, size, k=1.0, ang=0):
    if k <= 0.02:
        return
    f = FONT(int(size))
    l, t, r, b = f.getbbox("?")
    im = Image.new("RGBA", (r - l + 80, b - t + 80), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.text((40 - l, 40 - t), "?", font=f, fill=ACC, stroke_width=8, stroke_fill=INK)
    glow = im.filter(ImageFilter.GaussianBlur(18))
    im = Image.alpha_composite(glow, im)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k)))).rotate(ang, expand=True, resample=Image.BICUBIC)
    frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def sprite_paste(frame, im, x, y, ang=0, k=1.0):
    if k <= 0.02:
        return
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))))
    if ang:
        im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
    frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def bill_img(label="500"):
    im = Image.new("RGBA", (340, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, 334, 164], 16, fill=G[6], outline=INK, width=7)
    d.rounded_rectangle([24, 24, 316, 146], 10, outline=G[3], width=4)
    d.ellipse([125, 40, 215, 130], fill=ACC, outline=INK, width=5)
    f = FONT(44)
    d.text((40, 30), label, font=f, fill=INK)
    d.text((240, 92), label, font=f, fill=INK)
    return im


def clock(d, cx, cy, r, a_min, a_hour):
    d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=ACC, outline=INK, width=8)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=G[7], outline=INK, width=6)
    for i in range(12):
        a = i * math.pi / 6
        d.line([cx + (r - 30) * math.cos(a), cy + (r - 30) * math.sin(a), cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a)], fill=INK, width=8)
    d.line([cx, cy, cx + r * 0.5 * math.cos(a_hour), cy + r * 0.5 * math.sin(a_hour)], fill=INK, width=16)
    d.line([cx, cy, cx + r * 0.8 * math.cos(a_min), cy + r * 0.8 * math.sin(a_min)], fill=INK, width=10)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=ACC, outline=INK, width=4)


def mic(d, x0, y0, x1, y1):
    d.line([x0, y0, x1, y1], fill=INK, width=26)
    d.line([x0, y0, x1, y1], fill=G[1], width=16)
    d.ellipse([x1 - 30, y1 - 30, x1 + 30, y1 + 30], fill=G[5], outline=INK, width=6)
    d.line([x1 - 20, y1, x1 + 20, y1], fill=G[2], width=4)


def rain(frame, t, strength=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    rnd = random.Random(3)
    for _ in range(int(140 * strength)):
        x, y0, v = rnd.random() * W * 1.2, rnd.random() * H, rnd.uniform(1400, 2000)
        y = (y0 + v * t) % (H + 100) - 50
        xx = x - (y / H) * 160
        ld.line([xx, y, xx - 14, y + 46], fill=(220, 220, 230, 110), width=3)
    frame.alpha_composite(lay)


# ------------------------------------------------------------------ actions
def walk_away(c):
    return dict(extras=3, extras_x=120, hero_x=lambda lt: 560 + 700 * ease((lt - 0.4) / 1.8),
                pose="idle", walking=True,
                front=lambda fr, c: [bubble(ImageDraw.Draw(fr), 40 + i * 150, c["gy"] - 860 - (i % 2) * 70,
                                            eob((c["lt"] - 0.2 - i * 0.25) / 0.3), 190, 110) for i in range(3)])


def press(c):
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        rnd = random.Random(5)
        for i in range(6):  # micros qui arrivent des bords
            side = -1 if i % 2 else 1
            k = ease((c["lt"] - i * 0.12) / 0.4)
            tx = c["hx"] + side * (150 + rnd.randint(0, 60))
            ty = c["gy"] - 640 + rnd.randint(-120, 160)
            sx = tx + side * 600
            mic(d, sx, ty + 200, sx + (tx - sx) * k, ty + 200 + (ty - ty - 200) * k)
    def front(fr, c):
        k = eob((c["lt"] - 0.35) / 0.3)
        qmark(fr, c["hx"], c["gy"] - 1050 + 14 * math.sin(c["t"] * 5), 260, k, ang=8 * math.sin(c["t"] * 3))
    return dict(extras=0, hero_x=lambda lt: 540, pose="look", back=back, front=front)


def shrug(c):
    def front(fr, c):
        k = eob((c["lt"] - 0.2) / 0.3)
        qmark(fr, c["hx"] - 230, c["gy"] - 980, 140, k, ang=-14)
        qmark(fr, c["hx"] + 240, c["gy"] - 1020, 110, eob((c["lt"] - 0.4) / 0.3), ang=12)
    return dict(extras=0, hero_x=lambda lt: 540, pose="shrug", back=press(c)["back"], front=front)


def whisper(c):
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(3):
            k = eob((c["lt"] - 0.15 - i * 0.3) / 0.3)
            bubble(d, 420 + i * 170, c["gy"] - 900 - (i % 2) * 90, k, 170, 120, face=True)
    return dict(extras=3, extras_x=560, extras_look=-1, hero_x=lambda lt: 220, pose="look_r", front=front)


def with_them(c):
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        k = eob((c["lt"] - 0.3) / 0.3)
        bubble(d, 120, c["gy"] - 960, k, 220, 130)
        bubble(d, 640, c["gy"] - 930, eob((c["lt"] - 0.6) / 0.3), 220, 130, dark=False)
    return dict(extras=3, extras_x=560, hero_x=lambda lt: 300, pose="idle", front=front)


def envious(c):
    def front(fr, c):
        lay = Image.new("RGBA", (W, H), (10, 10, 12, int(170 * ease(c["lt"] / 0.4))))
        ld = ImageDraw.Draw(lay)
        rnd = random.Random(9)
        for i in range(11):
            x, y = rnd.randint(80, W - 80), rnd.randint(520, 1500)
            if abs(x - c["hx"]) < 160 and y > c["gy"] - 850:
                continue
            k = ease((c["lt"] - 0.1 - i * 0.08) / 0.2)
            bl = (c["t"] * 0.9 + i * 0.37) % 2.2 < 0.12
            h = 0 if bl else 34 * k
            look = 10 if x < c["hx"] else -10
            for sx in (-44, 44):
                ld.ellipse([x + sx - 34, y - h, x + sx + 34, y + h], fill=ACC + (255,))
                if not bl and k > 0.5:
                    ld.ellipse([x + sx + look * 1.6 - 12, y - 14, x + sx + look * 1.6 + 12, y + 14], fill=INK + (255,))
        fr.alpha_composite(lay)
    return dict(extras=0, hero_x=lambda lt: 540, pose="look", front=front, hero_on_top=True)


def rumors(c):
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        rnd = random.Random(11)
        for i in range(12):
            k = eob((c["lt"] - i * 0.12) / 0.25)
            x, y = rnd.randint(20, W - 280), rnd.randint(480, 1400)
            bubble(d, x, y + 8 * math.sin(c["t"] * 4 + i), k * rnd.uniform(0.6, 1.1), 240, 130, dark=i % 3 != 0)
    return dict(extras=4, extras_x=480, hero_x=lambda lt: 170, pose="look_r", front=front)


def target(c):
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        cx, cy = 720, c["gy"] - 760
        for i, col in enumerate([G[7], INK, G[7], ACC, G[7]]):
            r = 170 - i * 34
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=INK, width=5)
        k = ease((c["lt"] - 0.5) / 0.35)  # une seule flechette... a cote
        fx, fy = 300 + (cx + 210 - 300) * k, c["gy"] - 520 + (cy - 140 - c["gy"] + 520) * k - 160 * math.sin(math.pi * k)
        d.line([fx - 150, fy + 20, fx, fy], fill=INK, width=18)
        d.polygon([(fx - 150, fy + 20), (fx - 210, fy - 25), (fx - 195, fy + 65)], fill=ACC, outline=INK, width=5)
        if k >= 1:  # rate : petit "?" de deception
            d.text((fx - 40, fy - 150), "?", font=FONT(110), fill=ACC, stroke_width=6, stroke_fill=INK)
    return dict(extras=0, hero_x=lambda lt: 260, pose="idle", back=back)


def drama(c):
    return dict(extras=4, extras_x=380, extras_arms=True, hero_x=None, pose="idle")


def time_flies(c):
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        sp = c["t"] * 7
        clock(d, 540, 820, 230, sp, sp / 12)
        rnd = random.Random(13)
        for i in range(10):  # pages de calendrier qui s'envolent
            ph = (c["lt"] * 0.9 + i * 0.1) % 1
            x = rnd.randint(0, W) + 300 * ph
            y = 1500 - 1200 * ph + 40 * math.sin(c["t"] * 3 + i)
            im = Image.new("RGBA", (110, 120), (0, 0, 0, 0))
            dd = ImageDraw.Draw(im)
            dd.rectangle([4, 4, 106, 116], fill=G[7], outline=INK, width=5)
            dd.rectangle([4, 4, 106, 34], fill=ACC, outline=INK, width=5)
            dd.text((30, 44), str(rnd.randint(1, 31)), font=FONT(50), fill=INK)
            sprite_paste(fr, im, x, y, ang=(c["t"] * 140 + i * 40) % 360)
    return dict(extras=0, hero_x=lambda lt: 300, pose="look", back=back, hero_scale=0.8)


def hourglass(c):
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        cx, cy, hw, hh = 720, c["gy"] - 640, 150, 260
        f = min(1, c["lt"] / max(0.5, c["dur"]))
        d.rectangle([cx - hw - 30, cy - hh - 40, cx + hw + 30, cy - hh], fill=ACC, outline=INK, width=6)
        d.rectangle([cx - hw - 30, cy + hh, cx + hw + 30, cy + hh + 40], fill=ACC, outline=INK, width=6)
        d.polygon([(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + 14, cy), (cx + hw, cy + hh), (cx - hw, cy + hh), (cx - 14, cy)], fill=G[6], outline=INK)
        top = (1 - f) * 0.9
        d.polygon([(cx - hw * top, cy - hh * top), (cx + hw * top, cy - hh * top), (cx, cy)], fill=ACC)
        bot = f * 0.9
        d.polygon([(cx - hw, cy + hh), (cx + hw, cy + hh), (cx + hw * (1 - bot), cy + hh * (1 - bot)), (cx - hw * (1 - bot), cy + hh * (1 - bot))], fill=ACC)
        d.line([cx, cy, cx, cy + hh], fill=ACC, width=5)
        d.line([(cx - hw, cy - hh), (cx - 14, cy), (cx - hw, cy + hh)], fill=INK, width=7)
        d.line([(cx + hw, cy - hh), (cx + 14, cy), (cx + hw, cy + hh)], fill=INK, width=7)
    return dict(extras=0, hero_x=lambda lt: 260, pose="look", back=back)


def idea(c):
    def front(fr, c):
        k = eob((c["lt"] - 0.25) / 0.3)
        if k < 0.03:
            return
        x, y = c["hx"], c["gy"] - 1060
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        r = 260 * k * (1 + 0.1 * c["p"])
        ld.ellipse([x - r, y - r, x + r, y + r], fill=ACC + (90,))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(40)))
        d = ImageDraw.Draw(fr)
        r = 90 * k
        d.ellipse([x - r, y - r, x + r, y + r], fill=ACC, outline=INK, width=7)
        d.rectangle([x - 40 * k, y + r - 10, x + 40 * k, y + r + 50 * k], fill=G[4], outline=INK, width=6)
        for i in range(8):
            a = i * math.pi / 4 + c["t"]
            d.line([x + (r + 25) * math.cos(a), y + (r + 25) * math.sin(a), x + (r + 60 * k) * math.cos(a), y + (r + 60 * k) * math.sin(a)], fill=ACC, width=9)
    return dict(extras=0, hero_x=lambda lt: 540, pose="think", front=front)


def phone_call(c):
    def front(fr, c):
        k = eob((c["lt"] - 0.1) / 0.3)
        if k < 0.03:
            return
        sh = 8 * math.sin(c["t"] * 60) if (c["lt"] % 0.8) < 0.5 else 0
        im = Image.new("RGBA", (300, 520), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.rounded_rectangle([6, 6, 294, 514], 44, fill=INK)
        dd.rounded_rectangle([24, 40, 276, 470], 24, fill=G[6])
        b = bill_img().resize((220, 110))
        im.alpha_composite(b, (40, 150))
        dd.ellipse([110, 330, 190, 410], fill=ACC, outline=INK, width=6)
        x, y = 760 + sh, c["gy"] - 760
        sprite_paste(fr, im, x, y, ang=sh, k=k)
        d = ImageDraw.Draw(fr)
        for i in range(3):  # ondes de vibration
            r = 180 + i * 50 + 40 * ((c["t"] * 2) % 1)
            d.arc([x - r, y - r, x + r, y + r], -40, 40, fill=ACC, width=8)
            d.arc([x - r, y - r, x + r, y + r], 140, 220, fill=ACC, width=8)
    return dict(extras=0, hero_x=lambda lt: 280, pose="look_r", front=front)


def broken_link(c):
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        lt = c["lt"]
        y = c["gy"] - 330
        brk = ease((lt - 0.9) / 0.3)
        if brk < 1:
            d.line([c["hx"] + 150, y, 740 - 150, y], fill=ACC, width=16)
        else:
            d.line([c["hx"] + 150, y, 540 - 40, y + 60], fill=ACC, width=16)
            d.line([740 - 150, y, 540 + 40, y + 60], fill=ACC, width=16)
    def front(fr, c):
        lt = c["lt"]
        b = bill_img()
        for i in range(2):
            k = ease((lt - i * 0.25) / 0.8)
            sprite_paste(fr, b, 470 + i * 140, -200 + (c["gy"] - 620 + 200) * k, ang=(1 - k) * 200 + i * 20, k=0.75)
        if lt > 0.9:  # eclair de cassure
            d = ImageDraw.Draw(fr)
            x, y = 540, c["gy"] - 330
            pts = [(x - 20, y - 120), (x + 20, y - 40), (x - 20, y + 20), (x + 25, y + 110)]
            d.line(pts, fill=INK, width=14)
            d.line(pts, fill=G[7], width=6)
    return dict(extras=1, extras_x=760, hero_x=lambda lt: 280, pose="look_r", back=back, front=front)


def bigger_slice(c):
    def front(fr, c):
        d = ImageDraw.Draw(fr)
        cx, cy = 560, c["gy"] - 330
        d.ellipse([cx - 260, cy - 30, cx + 260, cy + 70], fill=G[6], outline=INK, width=6)  # assiette
        take = ease((c["lt"] - 0.4) / 1.0)
        # gateau vu de dessus : il reste la petite part, la grosse part glisse vers l'ami
        d.pieslice([cx - 200, cy - 110, cx + 200, cy + 110], 200, 300, fill=G[7], outline=INK, width=6)
        ox = 300 * take
        d.pieslice([cx - 200 + ox, cy - 110 - 20 * take, cx + 200 + ox, cy + 110 - 20 * take], 300, 200 + 360, fill=G[7], outline=INK, width=6)
        for a in (330, 30, 90, 140):
            r = math.radians(a)
            d.ellipse([cx + ox + 120 * math.cos(r) - 16, cy - 20 * take + 60 * math.sin(r) - 16, cx + ox + 120 * math.cos(r) + 16, cy - 20 * take + 60 * math.sin(r) + 16], fill=ACC, outline=INK, width=4)
        d.ellipse([cx + 90 * math.cos(math.radians(250)) - 16, cy + 50 * math.sin(math.radians(250)) - 16, cx + 90 * math.cos(math.radians(250)) + 16, cy + 50 * math.sin(math.radians(250)) + 16], fill=ACC, outline=INK, width=4)
    return dict(extras=1, extras_x=860, hero_x=lambda lt: 220, pose="look_r", front=front, table=True)


def alone(c):
    return dict(extras=0, hero_x=lambda lt: 540, pose="idle", front=lambda fr, c: rain(fr, c["t"]), dim=0.35)


def empty_seats(c):
    def back(fr, c):
        d = ImageDraw.Draw(fr)
        for i in range(5):
            x = 120 + i * 210
            if abs(x - 540) < 120:
                continue
            y = c["gy"]
            d.rectangle([x - 70, y - 300, x + 70, y - 290], fill=INK)
            d.rounded_rectangle([x - 70, y - 470, x + 70, y - 300], 16, fill=G[4], outline=INK, width=6)
            d.rounded_rectangle([x - 80, y - 300, x + 80, y - 250], 12, fill=G[5], outline=INK, width=6)
            for lx in (-60, 60):
                d.line([x + lx, y - 250, x + lx, y], fill=INK, width=12)
    def front(fr, c):
        qmark(fr, c["hx"] + 200 * math.sin(c["t"] * 2), c["gy"] - 1060, 170, eob((c["lt"] - 0.3) / 0.3))
    return dict(extras=0, hero_x=lambda lt: 540, pose="scan", back=back, front=front)


ACTIONS = {f.__name__: f for f in [walk_away, press, shrug, whisper, with_them, envious, rumors, target, drama,
                                   time_flies, hourglass, idea, phone_call, broken_link, bigger_slice, alone, empty_seats]}
