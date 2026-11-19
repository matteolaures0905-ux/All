#!/usr/bin/env python3
"""Generateur de lyric video verticale (format TikTok 1080x1920).

Usage :
  python3 make_video.py --lyrics paroles.json --audio son.mp3 --out video.mp4
  python3 make_video.py --lyrics paroles.srt  --audio son.mp3 --start 42 --duration 60

Sans --audio, les animations suivent un tempo fixe (--bpm).
Avec --audio, le fond et les mots "pulsent" sur l'energie du son.

Format JSON des paroles :
  [ {"start": 0.5, "end": 3.2, "text": "mon texte ici *MOT* fort"} , ... ]
  - les temps sont en secondes, relatifs au debut de l'extrait (--start)
  - un mot entre *etoiles* est mis en avant (plus gros, couleur flash)
  - optionnel : "words": [0.5, 0.9, 1.4, ...] = instant d'apparition de chaque mot
"""
import argparse, json, math, os, random, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
if not os.path.exists(FONT_BLACK):
    FONT_BLACK = FONT

PALETTES = [  # (fond A, fond B, accent, accent 2)
    ((255, 0, 110), (58, 12, 163), (255, 230, 0), (0, 245, 212)),
    ((0, 187, 249), (110, 0, 255), (255, 0, 140), (255, 230, 0)),
    ((255, 90, 0), (180, 0, 90), (0, 255, 170), (255, 255, 255)),
    ((0, 220, 130), (0, 70, 200), (255, 0, 200), (255, 230, 0)),
    ((140, 0, 255), (255, 0, 90), (0, 240, 255), (255, 210, 0)),
]


# ---------------------------------------------------------------- paroles
def parse_srt(path):
    txt = open(path, encoding="utf-8").read()
    out = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        lines = block.strip().splitlines()
        tl = next((l for l in lines if "-->" in l), None)
        if not tl:
            continue
        a, b = [s.strip() for s in tl.split("-->")]
        def ts(s):
            h, m, rest = s.replace(",", ".").split(":")
            return int(h) * 3600 + int(m) * 60 + float(rest)
        text = " ".join(lines[lines.index(tl) + 1:])
        out.append({"start": ts(a), "end": ts(b), "text": text})
    return out


def load_lyrics(path, offset):
    data = parse_srt(path) if path.endswith(".srt") else json.load(open(path, encoding="utf-8"))
    lines = []
    for item in data:
        s, e = item["start"] - offset, item["end"] - offset
        raw = item["text"].split()
        words = []
        times = item.get("words")
        for i, w in enumerate(raw):
            emph = w.startswith("*") and w.endswith("*") and len(w) > 2
            w = w.strip("*")
            t = times[i] - offset if times and i < len(times) else s + (e - s) * 0.85 * i / max(1, len(raw))
            words.append({"text": w.upper(), "t": t, "emph": emph})
        lines.append({"start": s, "end": e, "words": words})
    return lines


# ---------------------------------------------------------------- audio
def audio_energy(path, start, dur, fps):
    """Enveloppe d'energie normalisee (0..1) par image + detection de 'kicks'."""
    sr = 22050
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path,
           "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    pcm = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    hop = sr // fps
    n = int(dur * fps)
    pcm = np.pad(pcm, (0, max(0, n * hop - len(pcm))))
    frames = pcm[: n * hop].reshape(n, hop)
    # basses ~ moyenne glissante (filtre passe-bas grossier) pour attraper le kick
    k = 40
    low = np.convolve(pcm, np.ones(k) / k, mode="same")[: n * hop].reshape(n, hop)
    rms = np.sqrt((frames ** 2).mean(1))
    bass = np.sqrt((low ** 2).mean(1))
    def norm(x):
        x = x / (np.percentile(x, 98) + 1e-9)
        return np.clip(x, 0, 1)
    rms, bass = norm(rms), norm(bass)
    # impulsion : montee brutale des basses
    diff = np.clip(np.diff(bass, prepend=bass[0]), 0, None)
    pulse = np.zeros(n)
    v = 0.0
    for i in range(n):
        v = max(v * 0.82, min(1.0, diff[i] * 6))
        pulse[i] = v
    return rms, pulse


def bpm_energy(bpm, dur, fps):
    n = int(dur * fps)
    t = np.arange(n) / fps
    beat = (t * bpm / 60.0) % 1.0
    pulse = np.exp(-beat * 6)
    rms = 0.55 + 0.25 * np.exp(-((t * bpm / 120.0) % 1.0) * 3)
    return rms, pulse


# ---------------------------------------------------------------- rendu
_font_cache = {}
def font(size, black=False):
    key = (size, black)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_BLACK if black else FONT, size)
    return _font_cache[key]


_word_cache = {}
def word_sprite(text, size, fill, stroke, box=None, black=False):
    """Mot rendu une seule fois (contour epais + ombre), mis en cache."""
    key = (text, size, fill, stroke, box, black)
    if key in _word_cache:
        return _word_cache[key]
    f = font(size, black)
    sw = max(4, size // 11)
    l, t, r, b = f.getbbox(text, stroke_width=sw)
    pad = 30
    w, h = r - l + pad * 2, b - t + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if box:
        d.rounded_rectangle([pad - 18, pad - 8, w - pad + 18, h - pad + 8], radius=22, fill=box)
    else:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 8, pad - t + 10), text, font=f, fill=(0, 0, 0, 170),
                                stroke_width=sw, stroke_fill=(0, 0, 0, 170))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(6)))
        d = ImageDraw.Draw(img)
    d.text((pad - l, pad - t), text, font=f, fill=fill, stroke_width=0 if box else sw, stroke_fill=stroke)
    _word_cache[key] = img
    return img


def ease_out_back(x):
    c1, c3 = 2.2, 3.2
    x = min(max(x, 0), 1)
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def lerp(a, b, x):
    return tuple(int(a[i] + (b[i] - a[i]) * x) for i in range(3))


class Background:
    def __init__(self, seed=7):
        rnd = random.Random(seed)
        self.sw, self.sh = 108, 192  # basse resolution puis agrandi -> fluide et rapide
        yy, xx = np.mgrid[0:self.sh, 0:self.sw]
        self.xx, self.yy = xx / self.sw, yy / self.sh
        self.shapes = [{
            "x": rnd.random() * W, "y": rnd.random() * H, "r": rnd.uniform(18, 70),
            "vy": rnd.uniform(-90, -30), "rot": rnd.random() * 6.28, "vr": rnd.uniform(-2, 2),
            "kind": rnd.choice(["tri", "ring", "dot", "plus"]), "ci": rnd.randint(0, 3)}
            for _ in range(26)]

    def render(self, t, pal, pal_next, mix, energy, pulse):
        a = lerp(pal[0], pal_next[0], mix)
        b = lerp(pal[1], pal_next[1], mix)
        ang = t * 0.35
        g = (self.xx * math.cos(ang) + self.yy * math.sin(ang))
        g = 0.5 + 0.5 * np.sin(g * 3.0 + t * 0.9 + 1.5 * np.sin(self.yy * 4 + t * 0.6))
        img = np.empty((self.sh, self.sw, 3), np.float32)
        for c in range(3):
            img[..., c] = a[c] * g + b[c] * (1 - g)
        # vignette + flash sur les kicks
        v = 1 - 0.55 * ((self.xx - 0.5) ** 2 + (self.yy - 0.5) ** 2) * 2.2
        img *= v[..., None] * (0.75 + 0.35 * energy)
        img += 70 * pulse
        bg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        d = ImageDraw.Draw(bg, "RGBA")
        # rayons qui tournent depuis le centre
        cx, cy = W / 2, H * 0.47
        for i in range(12):
            th = t * 0.25 + i * math.pi / 6
            p = [(cx, cy),
                 (cx + 2400 * math.cos(th - 0.07), cy + 2400 * math.sin(th - 0.07)),
                 (cx + 2400 * math.cos(th + 0.07), cy + 2400 * math.sin(th + 0.07))]
            d.polygon(p, fill=(255, 255, 255, int(10 + 22 * pulse)))
        # formes flottantes
        cols = [pal[2], pal[3], (255, 255, 255), pal[0]]
        for s in self.shapes:
            y = (s["y"] + s["vy"] * t * (1 + energy)) % (H + 200) - 100
            x = s["x"] + 30 * math.sin(t + s["rot"])
            r = s["r"] * (1 + 0.35 * pulse)
            rot = s["rot"] + s["vr"] * t
            col = cols[s["ci"]] + (150,)
            if s["kind"] == "tri":
                pts = [(x + r * math.cos(rot + k * 2.094), y + r * math.sin(rot + k * 2.094)) for k in range(3)]
                d.polygon(pts, outline=col, width=6)
            elif s["kind"] == "ring":
                d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=7)
            elif s["kind"] == "dot":
                d.ellipse([x - r / 3, y - r / 3, x + r / 3, y + r / 3], fill=col)
            else:
                for k in range(2):
                    aa = rot + k * math.pi / 2
                    d.line([(x - r * math.cos(aa), y - r * math.sin(aa)),
                            (x + r * math.cos(aa), y + r * math.sin(aa))], fill=col, width=8)
        return bg


def layout_line(words, max_w, base):
    """Repartit les mots en rangees centrees."""
    rows, cur, cur_w = [], [], 0
    gap = base * 0.28
    for i, w in enumerate(words):
        size = int(base * (1.35 if w["emph"] else 1))
        ww = font(size, w["emph"]).getlength(w["text"])
        if cur and cur_w + gap + ww > max_w:
            rows.append(cur); cur, cur_w = [], 0
        cur.append((i, size, ww)); cur_w += ww + (gap if len(cur) > 1 else 0)
    if cur:
        rows.append(cur)
    return rows, gap


def draw_line(frame, line, t, li, pal, pulse, shake):
    words = line["words"]
    n_chars = sum(len(w["text"]) for w in words)
    base = 118 if n_chars < 22 else 100 if n_chars < 36 else 84
    rows, gap = layout_line(words, W - 140, base)
    row_h = base * 1.45
    y0 = H * 0.50 - len(rows) * row_h / 2
    # mot "actif" = dernier mot apparu
    active = max([i for i, w in enumerate(words) if w["t"] <= t] or [-1])
    out_k = min(1, max(0, (t - (line["end"] - 0.18)) / 0.18))  # sortie
    for r, row in enumerate(rows):
        total = sum(ww for _, _, ww in row) + gap * (len(row) - 1)
        x = (W - total) / 2
        cy = y0 + r * row_h + row_h / 2
        for i, size, ww in row:
            w = words[i]
            age = t - w["t"]
            if age < 0:
                x += ww + gap; continue
            k = ease_out_back(age / 0.22)
            scale = max(0.01, k * (1 + (0.12 * pulse if i == active else 0)) * (1 - out_k))
            if w["emph"]:
                spr = word_sprite(w["text"], size, (20, 10, 30), (0, 0, 0), box=pal[2] + (255,), black=True)
            elif i == active:
                spr = word_sprite(w["text"], size, pal[2], (0, 0, 0))
            else:
                spr = word_sprite(w["text"], size, (255, 255, 255), (0, 0, 0))
            sw, sh = spr.size
            s2 = spr.resize((max(1, int(sw * scale)), max(1, int(sh * scale))), Image.BILINEAR)
            ang = (-6 if (i + li) % 2 else 5) * (1 - min(1, age / 0.25)) + (3 * math.sin(t * 9) * shake if w["emph"] else 0)
            if abs(ang) > 0.3:
                s2 = s2.rotate(ang, resample=Image.BICUBIC, expand=True)
            dy = (1 - min(1, age / 0.18)) * 60
            px = int(x + ww / 2 - s2.size[0] / 2 + shake * random.uniform(-6, 6))
            py = int(cy - s2.size[1] / 2 + dy - out_k * 80 + shake * random.uniform(-6, 6))
            frame.alpha_composite(s2, (px, py))
            x += ww + gap


def draw_hud(frame, t, dur, pal, title, artist, pulse):
    d = ImageDraw.Draw(frame, "RGBA")
    # barre de progression
    d.rounded_rectangle([60, H - 210, W - 60, H - 196], radius=7, fill=(255, 255, 255, 70))
    d.rounded_rectangle([60, H - 210, 60 + (W - 120) * min(1, t / dur), H - 196], radius=7, fill=pal[2] + (255,))
    # carte titre en haut
    if title:
        f1, f2 = font(54, True), font(38)
        tw = max(f1.getlength(title), f2.getlength(artist or "")) + 90
        x0, y0 = (W - tw) / 2, 150
        d.rounded_rectangle([x0, y0, x0 + tw, y0 + 150], radius=34, fill=(0, 0, 0, 120))
        # mini egaliseur
        for k in range(5):
            hh = 14 + 34 * abs(math.sin(t * (5 + k) + k)) * (0.5 + pulse)
            d.rounded_rectangle([x0 + 22 + k * 11, y0 + 75 - hh / 2, x0 + 29 + k * 11, y0 + 75 + hh / 2], radius=3, fill=pal[2] + (255,))
        d.text((W / 2 + 30, y0 + 50), title, font=f1, fill=(255, 255, 255), anchor="mm")
        if artist:
            d.text((W / 2 + 30, y0 + 105), artist, font=f2, fill=pal[3], anchor="mm")


def intro(frame, t, pal):
    """Gros titre qui claque pendant la 1re seconde."""
    if t > 1.2:
        return
    k = ease_out_back(t / 0.35)
    fade = 1 - max(0, (t - 0.9) / 0.3)
    spr = word_sprite("PRÊT ?", 190, pal[2], (0, 0, 0), black=True)
    s = spr.resize((max(1, int(spr.width * k)), max(1, int(spr.height * k))))
    s.putalpha(s.getchannel("A").point(lambda a: int(a * fade)))
    frame.alpha_composite(s, (int(W / 2 - s.width / 2), int(H / 2 - s.height / 2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyrics", required=True)
    ap.add_argument("--audio")
    ap.add_argument("--start", type=float, default=0, help="debut de l'extrait dans le son (s)")
    ap.add_argument("--duration", type=float, default=60)
    ap.add_argument("--bpm", type=float, default=95)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--title", default="")
    ap.add_argument("--artist", default="")
    ap.add_argument("--out", default="video.mp4")
    a = ap.parse_args()

    fps, dur = a.fps, a.duration
    lines = load_lyrics(a.lyrics, a.start)
    rms, pulse = (audio_energy(a.audio, a.start, dur, fps) if a.audio else bpm_energy(a.bpm, dur, fps))
    bg = Background()

    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-"]
    if a.audio:
        cmd += ["-ss", str(a.start), "-t", str(dur), "-i", a.audio, "-c:a", "aac", "-b:a", "192k",
                "-af", f"afade=t=out:st={dur - 1.5}:d=1.5"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-shortest", a.out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    n = int(dur * fps)
    for fi in range(n):
        t = fi / fps
        # ligne courante -> palette (change a chaque ligne avec fondu)
        li = max([i for i, l in enumerate(lines) if l["start"] <= t] or [0])
        pal = PALETTES[li % len(PALETTES)]
        prev = PALETTES[(li - 1) % len(PALETTES)]
        since = t - (lines[li]["start"] if lines else 0)
        mix = min(1, since / 0.4)
        e, p = float(rms[fi]), float(pulse[fi])
        frame = bg.render(t, prev, pal, mix, e, p).convert("RGBA")
        # zoom "punch" sur les kicks
        if p > 0.05:
            z = 1 + 0.035 * p
            cw, ch = int(W / z), int(H / z)
            frame = frame.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H))
        draw_hud(frame, t, dur, pal, a.title, a.artist, p)
        intro(frame, t, pal)
        for l in lines:
            if l["start"] <= t < l["end"]:
                draw_line(frame, l, t, li, pal, p, shake=p if p > 0.4 else 0)
        # flash blanc sur gros kick
        if p > 0.7:
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(55 * (p - 0.7) / 0.3)))
            frame.alpha_composite(fl)
        enc.stdin.write(frame.convert("RGB").tobytes())
        if fi % (fps * 5) == 0:
            print(f"{t:5.1f}s / {dur:.0f}s", file=sys.stderr)
    enc.stdin.close()
    enc.wait()
    print("OK ->", a.out)


if __name__ == "__main__":
    main()
