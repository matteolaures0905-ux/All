#!/usr/bin/env python3
"""Lyric video "cartoon" : scenes dessinees en niveaux de gris + un accent jaune,
paroles karaoke en haut, mots forts en grand en orange, personnage anime.

  python3 make_cartoon.py --lyrics paroles.json --audio son.mp3 --start 45 --duration 60 --out video.mp4

Meme format de paroles que make_video.py (les mots entre *etoiles* sortent en grand).
Optionnel par ligne : "scene": "street" | "wall" | "park" | "stage" | "room" | "roof"
"""
import argparse, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_video import load_lyrics, audio_energy, bpm_energy, ease_out_back  # noqa: E402
import json

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
F_BOLD = os.path.join(HERE, "fonts", "oswald-latin-700-normal.woff")
F_SEMI = os.path.join(HERE, "fonts", "oswald-latin-600-normal.woff")

INK = (22, 22, 24)
ACC = (247, 176, 49)        # jaune-orange
ACC_D = (196, 128, 20)
G = [(30, 30, 32), (58, 58, 60), (88, 88, 90), (120, 120, 122), (152, 152, 154),
     (184, 184, 186), (214, 214, 216), (238, 238, 240)]
LW = 7  # epaisseur du contour

_fc = {}
def font(path, size):
    if (path, size) not in _fc:
        _fc[(path, size)] = ImageFont.truetype(path, size)
    return _fc[(path, size)]


# ------------------------------------------------------------------ decors
def sky(img, top, bot, y0=0, y1=H):
    a = np.linspace(0, 1, y1 - y0)[:, None, None]
    arr = (np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a)
    img.paste(Image.fromarray(np.repeat(arr, W, 1).astype(np.uint8)), (0, y0))


def grain(img, amount=10, seed=1):
    rng = np.random.default_rng(seed)
    arr = np.asarray(img).astype(np.int16)
    n = rng.integers(-amount, amount + 1, (H, W, 1))
    return Image.fromarray(np.clip(arr + n, 0, 255).astype(np.uint8))


def rect(d, box, fill, w=LW, r=0):
    if r:
        d.rounded_rectangle(box, r, fill=fill, outline=INK, width=w)
    else:
        d.rectangle(box, fill=fill, outline=INK, width=w)


def scene_street(rnd):
    img = Image.new("RGB", (W, H)); sky(img, G[2], G[4])
    d = ImageDraw.Draw(img)
    x = -40
    while x < W:  # immeubles du fond
        bw, bh = rnd.randint(140, 260), rnd.randint(380, 760)
        rect(d, [x, 1180 - bh, x + bw, 1200], G[rnd.choice([3, 4, 5])])
        for wy in range(1180 - bh + 40, 1140, 90):
            for wx in range(x + 25, x + bw - 40, 62):
                lit = rnd.random() < 0.18
                rect(d, [wx, wy, wx + 34, wy + 48], ACC if lit else G[1], w=4)
        x += bw + rnd.randint(-10, 20)
    rect(d, [-10, 1150, W + 10, 1260], G[5])          # mur bas
    for px in range(40, W, 210):                      # affiches
        rect(d, [px, 1000, px + 140, 1190], G[7], w=5)
        for ly in range(1030, 1170, 26):
            d.line([px + 20, ly, px + 120 - rnd.randint(0, 40), ly], fill=G[3], width=8)
    rect(d, [-10, 1250, W + 10, H + 10], G[3])        # trottoir
    for lx in range(-200, W + 200, 180):
        d.line([lx, 1250, lx - 260, H], fill=G[2], width=4)
    for bx in (90, 980):                              # potelets
        rect(d, [bx - 22, 1500, bx + 22, 1700], INK, r=18)
    return img


def scene_wall(rnd):
    img = Image.new("RGB", (W, H), G[2]); d = ImageDraw.Draw(img)
    bh, bw = 70, 170
    for row, y in enumerate(range(260, 1350, bh)):
        off = (row % 2) * bw // 2
        for x in range(-bw, W + bw, bw):
            c = G[rnd.choice([1, 2, 2, 3])]
            d.rectangle([x + off + 5, y + 5, x + off + bw - 5, y + bh - 5], fill=c, outline=G[0], width=3)
    rect(d, [-10, 1340, W + 10, H + 10], G[5])
    for x in range(0, W, 120):
        d.line([x, 1340, x, H], fill=G[4], width=3)
    return img


def scene_park(rnd):
    img = Image.new("RGB", (W, H)); sky(img, G[3], G[5])
    d = ImageDraw.Draw(img)
    for i, tx in enumerate(range(-60, W + 100, 230)):  # arbres ronds
        r = rnd.randint(130, 175); ty = 820 + rnd.randint(-60, 40)
        rect(d, [tx - 18, ty, tx + 18, 1250], G[1], w=5)
        d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=G[2 + i % 2], outline=INK, width=LW)
        d.arc([tx - r + 30, ty - r + 30, tx + r - 30, ty + r - 30], 200, 260, fill=G[4], width=8)
    rect(d, [-10, 1230, W + 10, H + 10], G[4])
    for _ in range(40):
        gx, gy = rnd.randint(0, W), rnd.randint(1260, H)
        d.line([gx, gy, gx + 8, gy - 22], fill=G[3], width=5)
    rect(d, [140, 1290, 940, 1330], G[6], r=8)        # banc
    rect(d, [140, 1360, 940, 1400], G[6], r=8)
    for lx in (190, 890):
        rect(d, [lx - 12, 1400, lx + 12, 1500], INK)
    rect(d, [1010, 700, 1030, 1300], INK)             # lampadaire
    d.ellipse([975, 650, 1065, 720], fill=ACC, outline=INK, width=LW)
    return img


def scene_stage(rnd):
    img = Image.new("RGB", (W, H), G[0]); d = ImageDraw.Draw(img)
    rect(d, [-10, 420, W + 10, 1420], G[2], w=0)
    for side in (0, 1):                               # rideaux
        for k in range(5):
            x0 = (k * 60) if side == 0 else W - (k + 1) * 60
            d.rectangle([x0, 400, x0 + 60, 1560], fill=G[1 if k % 2 else 0], outline=INK, width=3)
    d.rectangle([-10, 380, W + 10, 470], fill=G[0])
    for x in range(0, W + 60, 60):                    # festons jaunes
        d.arc([x - 30, 430, x + 30, 490], 0, 180, fill=ACC, width=7)
    d.line([0, 460, W, 460], fill=ACC, width=7)
    rect(d, [-10, 1420, W + 10, 1560], G[4])          # scene
    d.line([0, 1420, W, 1420], fill=ACC, width=8)
    rect(d, [-10, 1560, W + 10, H + 10], G[0], w=0)
    for i in range(14):                               # public
        hx, hy = 40 + i * 78 + rnd.randint(-10, 10), 1720 + (i % 3) * 30
        d.ellipse([hx - 45, hy - 45, hx + 45, hy + 45], fill=G[1])
        d.rounded_rectangle([hx - 70, hy + 30, hx + 70, H + 40], 40, fill=G[1])
    return img


def scene_room(rnd):
    img = Image.new("RGB", (W, H)); sky(img, G[1], G[3])
    d = ImageDraw.Draw(img)
    rect(d, [330, 760, 750, 1080], ACC, w=LW)         # cadre
    rect(d, [360, 790, 720, 1050], G[5], w=4)
    d.ellipse([420, 860, 520, 960], fill=G[2]); d.rounded_rectangle([395, 960, 545, 1050], 40, fill=G[2])
    d.ellipse([560, 850, 670, 960], fill=G[3]); d.rounded_rectangle([535, 960, 695, 1050], 40, fill=G[3])
    rect(d, [-10, 1300, W + 10, 1400], G[6])          # table
    rect(d, [-10, 1400, W + 10, H + 10], G[2])
    d.line([W // 2, 0, W // 2, 470], fill=INK, width=6)  # lampe
    d.polygon([(W // 2 - 110, 590), (W // 2 + 110, 590), (W // 2 + 60, 470), (W // 2 - 60, 470)],
              fill=G[0], outline=INK)
    return img


def scene_roof(rnd):
    img = Image.new("RGB", (W, H)); sky(img, (18, 18, 22), G[2])
    d = ImageDraw.Draw(img)
    for _ in range(70):
        sx, sy = rnd.randint(0, W), rnd.randint(300, 1000)
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=G[6])
    d.ellipse([720, 420, 900, 600], fill=G[7], outline=INK, width=LW)
    d.ellipse([760, 470, 800, 510], fill=G[5]); d.ellipse([820, 530, 850, 560], fill=G[5])
    x = -30
    while x < W:
        bw, bh = rnd.randint(90, 200), rnd.randint(150, 420)
        d.rectangle([x, 1150 - bh, x + bw, 1160], fill=G[0])
        for wy in range(1170 - bh, 1130, 55):
            for wx in range(x + 18, x + bw - 20, 40):
                if rnd.random() < 0.22:
                    d.rectangle([wx, wy, wx + 16, wy + 22], fill=ACC)
        x += bw
    rect(d, [-10, 1150, W + 10, H + 10], G[3])
    rect(d, [-10, 1150, W + 10, 1200], G[5])
    return img


SCENES = {"street": scene_street, "wall": scene_wall, "park": scene_park,
          "stage": scene_stage, "room": scene_room, "roof": scene_roof}
ORDER = ["street", "wall", "park", "room", "stage", "roof"]
GROUND = {"street": 1690, "wall": 1650, "park": 1640, "stage": 1530, "room": 1700, "roof": 1640}


# ------------------------------------------------------------------ personnages
def draw_hero(d, cx, gy, t, talk, s=1.0, step=0.0, look=0.0):
    """Personnage original : casquette jaune a l'envers, sweat a capuche gris, baskets blanches."""
    bob = 6 * math.sin(t * 6) * s
    def P(x, y): return (cx + x * s, gy + y * s + (bob if y < -200 else 0))
    sw = math.sin(step * 8) * 26
    # jambes + baskets
    for side, ph in ((-1, 1), (1, -1)):
        lx = 38 * side + sw * ph * (1 if step else 0)
        d.rounded_rectangle([*P(lx - 30, -260), *P(lx + 30, -40)], int(14 * s), fill=G[1], outline=INK, width=LW)
        d.rounded_rectangle([*P(lx - 46, -55), *P(lx + 50, 0)], int(22 * s), fill=G[7], outline=INK, width=LW)
        d.line([P(lx - 40, -16), P(lx + 44, -16)], fill=ACC, width=int(8 * s))
    # corps (sweat)
    d.rounded_rectangle([*P(-125, -560), *P(125, -230)], int(70 * s), fill=G[4], outline=INK, width=LW)
    d.rounded_rectangle([*P(-70, -360), *P(70, -280)], int(20 * s), fill=G[3], outline=INK, width=5)  # poche
    for k in (-1, 1):  # cordons
        d.line([P(22 * k, -540), P(26 * k, -450)], fill=ACC, width=int(8 * s))
        d.ellipse([*P(26 * k - 9, -458), *P(26 * k + 9, -440)], fill=ACC)
    # bras
    arm = 12 * math.sin(t * 6 + 1) + (40 if talk > 0.55 else 0)
    for k in (-1, 1):
        a0 = P(118 * k, -520)
        a1 = P((150 + (arm if k == 1 else 0) * 0.6) * k, -330 - (arm if k == 1 else 0) * 1.6)
        d.line([a0, a1], fill=INK, width=int(64 * s))
        d.line([a0, a1], fill=G[4], width=int(50 * s))
        d.ellipse([a1[0] - 28 * s, a1[1] - 28 * s, a1[0] + 28 * s, a1[1] + 28 * s], fill=G[6], outline=INK, width=LW)
    # capuche derriere la tete
    d.ellipse([*P(-150, -640), *P(150, -500)], fill=G[3], outline=INK, width=LW)
    # tete
    hx0, hy0, hx1, hy1 = *P(-115, -820), *P(115, -560)
    d.ellipse([hx0, hy0, hx1, hy1], fill=G[6], outline=INK, width=LW)
    # yeux (clignent)
    blink = (t % 3.7) < 0.12
    ex = 42 + look * 12
    for k in (-1, 1):
        x, y = P(ex * k + look * 18, -700)
        if blink:
            d.line([x - 16 * s, y, x + 16 * s, y], fill=INK, width=int(7 * s))
        else:
            d.ellipse([x - 15 * s, y - 20 * s, x + 15 * s, y + 20 * s], fill=INK)
            d.ellipse([x - 4 * s, y - 14 * s, x + 6 * s, y - 4 * s], fill=G[7])
    # bouche qui suit la voix
    mx, my = P(look * 18, -628)
    mo = 6 + 30 * talk
    d.rounded_rectangle([mx - 32 * s, my - mo * s / 2, mx + 32 * s, my + mo * s / 2], int(14 * s), fill=INK)
    # casquette a l'envers
    d.chord([*P(-120, -840), *P(120, -640)], 180, 360, fill=ACC, outline=INK, width=LW)
    d.rounded_rectangle([*P(-160, -760), *P(-80, -730)], int(12 * s), fill=ACC_D, outline=INK, width=5)
    d.line([P(-100, -760), P(100, -760)], fill=INK, width=5)


def draw_extra(d, cx, gy, s, shade, t, ph):
    """Silhouette secondaire simple."""
    b = 4 * math.sin(t * 5 + ph)
    d.rounded_rectangle([cx - 85 * s, gy - 470 * s + b, cx + 85 * s, gy - 200 * s], int(50 * s), fill=G[shade], outline=INK, width=LW)
    for k in (-1, 1):
        d.rounded_rectangle([cx + (28 * k - 22) * s, gy - 220 * s, cx + (28 * k + 22) * s, gy], int(10 * s), fill=G[0], outline=INK, width=LW)
    d.ellipse([cx - 70 * s, gy - 620 * s + b, cx + 70 * s, gy - 460 * s + b], fill=G[5], outline=INK, width=LW)
    for k in (-1, 1):
        d.ellipse([cx + 25 * k * s - 9 * s, gy - 555 * s + b, cx + 25 * k * s + 9 * s, gy - 535 * s + b], fill=INK)
    d.chord([cx - 72 * s, gy - 630 * s + b, cx + 72 * s, gy - 520 * s + b], 180, 360, fill=G[shade - 1 if shade > 0 else 0], outline=INK, width=LW)


# ------------------------------------------------------------------ texte
def wrap(words, f, maxw):
    rows, cur = [], []
    for w in words:
        test = " ".join(x["text"] for x in cur + [w])
        if cur and f.getlength(test) > maxw:
            rows.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur:
        rows.append(cur)
    return rows


def draw_lyrics(frame, line, t, pulse):
    d = ImageDraw.Draw(frame)
    top = line["words"]
    emph = [w for w in line["words"] if w["emph"]]
    n = sum(len(w["text"]) for w in top)
    size = 76 if n < 26 else 66 if n < 40 else 58
    f = font(F_BOLD, size)
    rows = wrap(top, f, W - 160)
    y = 250 - (len(rows) - 1) * size * 0.62
    out = min(1, max(0, (t - (line["end"] - 0.15)) / 0.15))
    for row in rows:
        total = f.getlength(" ".join(w["text"] for w in row))
        x = (W - total) / 2
        for w in row:
            on = t >= w["t"]
            col = (ACC if w["emph"] else (250, 250, 250)) if on else (150, 150, 152)
            age = t - w["t"]
            lift = -10 * (1 - min(1, age / 0.12)) if 0 <= age < 0.12 else 0
            if out:
                col = tuple(int(c * (1 - out) + 40 * out) for c in col)
            d.text((x + 4, y + 6 + lift), w["text"], font=f, fill=(0, 0, 0))
            d.text((x, y + lift), w["text"], font=f, fill=col)
            x += f.getlength(w["text"] + " ")
        y += size * 1.25
    # mot fort en grand
    for w in emph:
        age = t - w["t"]
        if age < 0:
            continue
        k = ease_out_back(age / 0.25) * (1 - out) * (1 + 0.06 * pulse)
        size2 = 190 if len(w["text"]) < 8 else 150 if len(w["text"]) < 11 else 120
        f2 = font(F_BOLD, size2)
        l, tt, r, b = f2.getbbox(w["text"])
        tw, th = r - l + 120, b - tt + 120
        spr = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        sd = ImageDraw.Draw(spr)
        sd.text((60 - l, 60 - tt), w["text"], font=f2, fill=ACC + (200,))
        glow = spr.filter(ImageFilter.GaussianBlur(22))
        spr2 = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        s2 = ImageDraw.Draw(spr2)
        s2.text((60 - l + 6, 60 - tt + 8), w["text"], font=f2, fill=(0, 0, 0, 200))
        s2.text((60 - l, 60 - tt), w["text"], font=f2, fill=ACC + (255,))
        spr = Image.alpha_composite(glow, spr2)
        sz = (max(1, int(tw * k)), max(1, int(th * k)))
        spr = spr.resize(sz, Image.BILINEAR)
        cy = 250 + len(rows) * size * 1.25 + 90
        frame.alpha_composite(spr, (int(W / 2 - sz[0] / 2), int(cy - sz[1] / 2)))
        break


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyrics", required=True)
    ap.add_argument("--audio")
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--duration", type=float, default=60)
    ap.add_argument("--bpm", type=float, default=95)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", default="video_cartoon.mp4")
    a = ap.parse_args()
    fps, dur = a.fps, a.duration

    lines = load_lyrics(a.lyrics, a.start)
    raw = json.load(open(a.lyrics, encoding="utf-8")) if a.lyrics.endswith(".json") else [{} for _ in lines]
    for i, l in enumerate(lines):
        l["scene"] = raw[i].get("scene") or ORDER[i % len(ORDER)]
        l["seed"] = i
    rms, pulse = audio_energy(a.audio, a.start, dur, fps) if a.audio else bpm_energy(a.bpm, dur, fps)
    # la bouche suit l'energie lissee pendant qu'une ligne est chantee
    talk_env = np.convolve(rms, np.ones(3) / 3, "same")

    cache = {}
    def bg_for(l):
        key = (l["scene"], l["seed"] % 2)
        if key not in cache:
            img = SCENES[l["scene"]](random.Random(hash(key) & 0xffff))
            # bandeau sombre en haut pour les paroles
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            for y in range(0, 640):
                a_ = 1.0 if y < 380 else max(0, 1 - (y - 380) / 260) ** 1.3
                od.line([0, y, W, y], fill=(30, 30, 32, int(250 * a_)))
            cache[key] = grain(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), 7, len(cache))
        return cache[key]

    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-"]
    if a.audio:
        cmd += ["-ss", str(a.start), "-t", str(dur), "-i", a.audio, "-c:a", "aac", "-b:a", "192k",
                "-af", f"afade=t=out:st={dur - 1.2}:d=1.2"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-shortest", a.out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    dust = [(random.random() * W, random.random() * H, random.uniform(2, 5), random.uniform(10, 35)) for _ in range(45)]

    for fi in range(int(dur * fps)):
        t = fi / fps
        cur = [i for i, l in enumerate(lines) if l["start"] - 0.25 <= t]
        li = cur[-1] if cur else 0
        line = lines[li]
        scene = line["scene"]
        frame = bg_for(line).copy().convert("RGBA")
        d = ImageDraw.Draw(frame)
        lt = t - (line["start"] - 0.25)
        p = float(pulse[fi])
        singing = any(l["start"] <= t < l["end"] for l in lines)
        talk = float(talk_env[fi]) if singing else 0.05
        gy = GROUND[scene]
        rnd = random.Random(line["seed"])

        # lumiere
        if scene in ("wall", "stage", "room"):
            cx = W // 2 if scene != "stage" else 400
            topy = 590 if scene == "room" else 470
            a_ = int(55 + 30 * math.sin(t * 3) + 50 * p)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(lay).polygon([(cx - 70, topy), (cx + 70, topy), (cx + 420, gy), (cx - 420, gy)], fill=ACC + (a_,))
            frame.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
            d = ImageDraw.Draw(frame)
            if scene == "room":
                d.ellipse([cx - 40, 570, cx + 40, 610], fill=ACC + (255,))
        # figurants
        n_ex = {"street": 3, "park": 2, "stage": 3, "roof": 0, "wall": 0, "room": 1}[scene]
        for k in range(n_ex):
            ex = 560 + k * 170 + rnd.randint(-20, 20)
            draw_extra(d, ex, gy - 10 - k * 6, 0.82 - k * 0.04, rnd.choice([1, 2, 5, 6]), t, k)
        # heros : entre en marchant au debut de la scene "street"
        hx = 300
        step = 0.0
        if scene == "street" and lt < 0.9:
            hx = -150 + 450 * min(1, lt / 0.9); step = t
        draw_hero(d, hx, gy, t, talk, s=0.95, step=step, look=0.6 if n_ex else 0)
        # bulle de dialogue sur les lignes paires
        if li % 3 == 1 and lt > 0.3:
            k = ease_out_back((lt - 0.3) / 0.25)
            bx, by = hx + 120, gy - 900
            d.rounded_rectangle([bx, by, bx + 260 * k, by + 140 * k], int(40 * k) + 1, fill=G[0] + (255,), outline=G[7] + (255,), width=6)
            for r in range(3):
                d.line([bx + 40 * k, by + (35 + r * 35) * k, bx + (220 - r * 50) * k, by + (35 + r * 35) * k], fill=G[7], width=max(1, int(12 * k)))
        # poussieres
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for (x, y, r, v) in dust:
            yy = (y - v * t) % H
            ld.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 255, 255, 70))
        frame.alpha_composite(lay)

        # camera : leger zoom continu + punch sur le kick + petite secousse a la coupe
        z = 1.0 + 0.04 * min(1, lt / 4) + 0.02 * p + (0.05 * (1 - lt / 0.2) if lt < 0.2 else 0)
        cw, ch = int(W / z), int(H / z)
        ox = (W - cw) // 2 + int(6 * p * math.sin(t * 50))
        oy = int((H - ch) * 0.65)
        frame = frame.crop((ox, oy, ox + cw, oy + ch)).resize((W, H), Image.BILINEAR)
        for l in lines:
            if l["start"] - 0.25 <= t < l["end"]:
                draw_lyrics(frame, l, t, p)
                break
        enc.stdin.write(frame.convert("RGB").tobytes())
        if fi % (fps * 10) == 0:
            print(f"{t:5.1f}s / {dur:.0f}s", file=sys.stderr)
    enc.stdin.close(); enc.wait()
    print("OK ->", a.out)


if __name__ == "__main__":
    main()
