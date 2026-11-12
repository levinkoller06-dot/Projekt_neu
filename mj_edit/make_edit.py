"""Michael-Jackson-Edit (hochkant, 1080x1920, 30 fps).

Ohne Clip:   python3 make_edit.py
Mit Clip:    python3 make_edit.py --clip moonwalk.mp4            (nimmt 3:37-3:42)
             python3 make_edit.py --clip schnitt.mp4 --start 0   (schon geschnitten)

Aufbau: Intro (gruener Mond) -> Player-Ansicht, Lied wird eingeschaltet ->
        echter Clip (oder Beat-Cuts, wenn kein Clip da ist) -> Outro.
"""
import argparse
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
BEAT = 60 / 117  # Billie Jean: 117 BPM
FONT_DIR = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    try:
        return ImageFont.truetype(FONT_DIR + name, size)
    except OSError:
        return ImageFont.load_default(size)


def load(name):
    return Image.open(os.path.join(HERE, "assets", name)).convert("RGB")


COVER = load("cover.png")
MOON = load("moon.png")

# ---------- Helfer ----------
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
ease_out = lambda x: 1 - (1 - clamp(x)) ** 3
ease_io = lambda x: (lambda v: v * v * (3 - 2 * v))(clamp(x))


def fill(img, zoom=1.0, cx=0.5, cy=0.5, size=(W, H)):
    """Bild formatfuellend zuschneiden, zoom >= 1, Mittelpunkt cx/cy (0..1)."""
    w, h = size
    iw, ih = img.size
    s = max(w / iw, h / ih) * zoom
    cw, ch = w / s, h / s
    x0 = clamp(cx * iw - cw / 2, 0, iw - cw)
    y0 = clamp(cy * ih - ch / 2, 0, ih - ch)
    return img.resize(size, Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def sharpen(img):
    return img.filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))


def rgb_split(img, d):
    if d < 1:
        return img
    r, g, b = img.split()
    return Image.merge("RGB", (ImageChops.offset(r, int(d), 0), g, ImageChops.offset(b, -int(d), 0)))


def tint(img, color, amount):
    return Image.blend(img, Image.new("RGB", img.size, color), clamp(amount)) if amount > 0 else img


def zoom_frame(img, z, cx=W / 2, cy=H / 2):
    if z <= 1.001:
        return img
    cw, ch = W / z, H / z
    x0 = clamp(cx - cw / 2, 0, W - cw)
    y0 = clamp(cy - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


_yy, _xx = np.mgrid[0:H, 0:W]
_d = np.hypot((_xx - W / 2) / (W / 2), (_yy - H / 2) / (H / 2))
VIGNETTE = Image.fromarray((255 * np.clip(1.15 - 0.45 * _d ** 2, 0, 1)).astype(np.uint8)).convert("RGB")
_rng = np.random.default_rng(7)
GRAIN = [Image.fromarray(_rng.integers(118, 138, (H // 2, W // 2), dtype=np.uint8)).resize((W, H)).convert("RGB")
         for _ in range(6)]


def finish(img, i):
    img = ImageChops.multiply(img, VIGNETTE)
    return ImageChops.overlay(img, GRAIN[i % len(GRAIN)])


def text_center(d, y, s, f, fill_, spacing=0):
    if spacing:
        total = sum(d.textlength(c, font=f) for c in s) + spacing * (len(s) - 1)
        x = (W - total) / 2
        for c in s:
            d.text((x, y), c, font=f, fill=fill_)
            x += d.textlength(c, font=f) + spacing
    else:
        d.text((W / 2, y), s, font=f, fill=fill_, anchor="ma")


# ---------- Szene 1: Intro ----------
MOON_S = sharpen(fill(MOON, 1.0))


def scene_intro(t, dur):
    p = t / dur
    img = zoom_frame(MOON_S, 1.0 + 0.10 * p)
    pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi / BEAT)
    glow = img.filter(ImageFilter.GaussianBlur(30)) if int(t * FPS) % 2 == 0 else img
    img = ImageChops.screen(img, tint(glow, (0, 0, 0), 1 - 0.35 * pulse))
    # Glitch-Einblendung
    if t < 0.5:
        img = rgb_split(img, 30 * (1 - t / 0.5))
        img = tint(img, (0, 0, 0), 1 - ease_out(t / 0.4))
        if int(t * FPS) in (3, 4, 9):
            img = ImageChops.offset(img, 40, 0)
    if t > dur - 0.2:
        img = tint(img, (255, 255, 255), (t - (dur - 0.2)) / 0.2)
    return img


# ---------- Szene 2: Player ----------
COVER_BIG = sharpen(COVER.resize((920, 920), Image.LANCZOS))
PLAYER_BG = fill(COVER, 1.4).filter(ImageFilter.GaussianBlur(90))
PLAYER_BG = tint(PLAYER_BG, (0, 0, 0), 0.45)
_grad = Image.fromarray(np.tile(np.linspace(40, 215, H).astype(np.uint8)[:, None], (1, W)))
PLAYER_BG = Image.composite(Image.new("RGB", (W, H), (10, 10, 10)), PLAYER_BG, _grad)
F_T, F_A, F_S, F_X = font("Inter-Bold.otf", 62), font("Inter-Medium.otf", 40), font("Inter-Medium.otf", 30), font("Inter-Bold.otf", 30)
GREEN = (30, 215, 96)
TAP = 1.35  # Sekunde in der Szene, in der Play gedrueckt wird


def rounded(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.size[0] - 1, img.size[1] - 1), r, fill=255)
    return m


def scene_player(t, dur):
    img = PLAYER_BG.copy()
    d = ImageDraw.Draw(img, "RGBA")
    playing = t >= TAP
    since = t - TAP

    # Kopfzeile
    d.line([(70, 150), (92, 172), (114, 150)], fill=(255, 255, 255), width=6, joint="curve")
    text_center(d, 128, "WIRD ABGESPIELT VOM ALBUM", font("Inter-Medium.otf", 24), (200, 200, 200), 3)
    text_center(d, 164, "Thriller", F_X, (255, 255, 255))
    for k in range(3):
        d.ellipse((1000 - 6, 146 + k * 16 - 4, 1000 + 6, 146 + k * 16 + 8), fill=(255, 255, 255))

    # Cover: klein im Pause-Zustand, waechst beim Einschalten
    s = 0.86 + 0.14 * ease_out(since / 0.45) if playing else 0.86
    if playing:
        s += 0.012 * max(0, math.sin(since * 2 * math.pi / BEAT)) ** 4
    size = int(920 * s)
    cov = COVER_BIG.resize((size, size), Image.LANCZOS)
    cx, cy = W // 2, 330 + 460
    sh = Image.new("RGBA", (size + 240, size + 240), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((120, 140, size + 120, size + 140), 30, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(45))
    img.paste(sh, (cx - size // 2 - 120, cy - size // 2 - 120), sh)
    img.paste(cov, (cx - size // 2, cy - size // 2), rounded(cov, 26))
    d = ImageDraw.Draw(img, "RGBA")

    # Titel
    d.text((80, 1335), "Billie Jean", font=F_T, fill=(255, 255, 255))
    d.text((80, 1418), "Michael Jackson", font=F_A, fill=(190, 190, 190))
    d.ellipse((940, 1362, 1000, 1422), fill=GREEN)
    d.line([(955, 1393), (966, 1404), (986, 1381)], fill=(0, 0, 0), width=6, joint="curve")

    # Fortschritt
    sec = max(0.0, since) if playing else 0.0
    px = 80 + (W - 160) * sec / 294
    d.rounded_rectangle((80, 1522, W - 80, 1530), 4, fill=(255, 255, 255, 70))
    d.rounded_rectangle((80, 1522, max(px, 88), 1530), 4, fill=(255, 255, 255))
    d.ellipse((px - 12, 1514, px + 12, 1538), fill=(255, 255, 255))
    d.text((80, 1550), "0:%02d" % int(sec), font=F_S, fill=(190, 190, 190))
    d.text((W - 80, 1550), "-4:%02d" % (54 - int(sec)), font=F_S, fill=(190, 190, 190), anchor="ra")

    # Steuerung
    y = 1720
    wh = (255, 255, 255)
    # Shuffle / Repeat (vereinfacht)
    d.line([(90, y - 18), (120, y - 18), (150, y + 18), (176, y + 18)], fill=GREEN, width=6, joint="curve")
    d.line([(90, y + 18), (120, y + 18), (150, y - 18), (176, y - 18)], fill=GREEN, width=6, joint="curve")
    d.rounded_rectangle((910, y - 22, 990, y + 22), 20, outline=wh, width=6)
    # Zurueck / Vor
    d.rectangle((290, y - 28, 300, y + 28), fill=wh)
    d.polygon([(352, y - 28), (352, y + 28), (304, y)], fill=wh)
    d.rectangle((780, y - 28, 790, y + 28), fill=wh)
    d.polygon([(728, y - 28), (728, y + 28), (776, y)], fill=wh)
    # Play/Pause-Knopf mit Druck-Animation
    press = math.exp(-((t - TAP) / 0.09) ** 2)
    r = 86 * (1 - 0.12 * press)
    d.ellipse((W / 2 - r, y - r, W / 2 + r, y + r), fill=wh)
    if playing:
        d.rounded_rectangle((W / 2 - 28, y - 32, W / 2 - 8, y + 32), 4, fill=(0, 0, 0))
        d.rounded_rectangle((W / 2 + 8, y - 32, W / 2 + 28, y + 32), 4, fill=(0, 0, 0))
    else:
        d.polygon([(W / 2 - 22, y - 36), (W / 2 - 22, y + 36), (W / 2 + 40, y)], fill=(0, 0, 0))
    # Finger-Tipp + Welle
    if TAP - 0.35 < t < TAP + 0.5:
        a = int(150 * clamp((t - (TAP - 0.35)) / 0.2) * clamp((TAP + 0.5 - t) / 0.35))
        rr = 46 + (140 * ease_out(since / 0.5) if playing else 0)
        d.ellipse((W / 2 - rr, y - rr, W / 2 + rr, y + rr), fill=(255, 255, 255, a // 2 if playing else a),
                  outline=(255, 255, 255, a), width=4)
    # Equalizer neben dem Titel, sobald es laeuft
    if playing:
        for k in range(4):
            hgt = 10 + 34 * abs(math.sin(since * (7 + 2.3 * k) + k))
            d.rounded_rectangle((820 + k * 16, 1412 - hgt, 830 + k * 16, 1412), 3, fill=GREEN)

    # Einfahrt von unten
    if t < 0.5:
        off = int(H * (1 - ease_out(t / 0.5)))
        base = Image.new("RGB", (W, H), (0, 0, 0))
        base.paste(img, (0, off))
        img = base
    if playing and since < 0.25:
        img = rgb_split(img, 14 * (1 - since / 0.25))
    # Ausfahrt: Zoom ins Cover + Blitz
    out = dur - t
    if out < 0.45:
        q = 1 - out / 0.45
        img = zoom_frame(img, 1 + 1.6 * q * q, cx, cy - 120)
        img = tint(img, (255, 255, 255), q ** 3)
    return img


# ---------- Szene 3: echter Clip oder Beat-Cuts ----------
COVER_S = sharpen(COVER.resize((1400, 1400), Image.LANCZOS))
SHOTS = [  # (Quelle, zoom, cx, cy)
    (COVER_S, 1.0, 0.56, 0.5), (COVER_S, 2.1, 0.60, 0.26), (MOON_S, 1.0, 0.5, 0.5), (COVER_S, 1.5, 0.45, 0.62),
    (COVER_S, 2.6, 0.62, 0.22), (MOON_S, 1.6, 0.6, 0.35), (COVER_S, 1.25, 0.6, 0.4), (COVER_S, 1.9, 0.3, 0.2),
    (COVER_S, 1.1, 0.5, 0.5), (COVER_S, 2.3, 0.6, 0.28),
]
WORDS = ["BILLIE", "JEAN", "", "THE KING", "OF POP", "", "THRILLER", "1982", "", "MJ"]
F_BIG = font("Inter-Black.otf", 190)


def scene_cuts(t, dur):
    k = min(int(t / BEAT), len(SHOTS) - 1)
    lt = t - k * BEAT
    src, z, cx, cy = SHOTS[k]
    punch = 0.10 * math.exp(-lt / 0.12)
    img = fill(src, z * (1.0 + 0.05 * lt / BEAT + punch), cx, cy)
    if k % 4 == 3:
        img = ImageChops.invert(img) if lt < 0.07 else img
    if k % 2 == 1 and src is COVER_S:
        img = Image.merge("RGB", [img.convert("L")] * 3)
        img = ImageChops.multiply(img, Image.new("RGB", (W, H), (255, 235, 215)))
    img = rgb_split(img, 22 * math.exp(-lt / 0.08))
    img = tint(img, (255, 255, 255), 0.75 * math.exp(-lt / 0.05))
    word = WORDS[k]
    if word:
        f = F_BIG if len(word) < 7 else font("Inter-Black.otf", 150)
        d = ImageDraw.Draw(img)
        yy = 1430 - 30 * ease_out(lt / 0.2)
        d.text((W / 2, yy), word, font=f, anchor="ma", fill=None, stroke_width=5, stroke_fill=(255, 255, 255))
    return img


class Clip:
    def __init__(self, path, start, dur):
        vf = f"fps={FPS},scale=-2:{H},crop={W}:{H},eq=contrast=1.08:saturation=1.1"
        cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path,
               "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        raw = subprocess.run(cmd, capture_output=True, check=True).stdout
        n = len(raw) // (W * H * 3)
        if n == 0:
            raise SystemExit("Clip liefert keine Bilder - Pfad/Startzeit pruefen.")
        self.frames = np.frombuffer(raw[: n * W * H * 3], np.uint8).reshape(n, H, W, 3)

    def scene(self, t, dur):
        i = min(int(t * FPS), len(self.frames) - 1)
        img = Image.fromarray(self.frames[i])
        img = zoom_frame(img, 1.0 + 0.12 * math.exp(-t / 0.15))
        img = rgb_split(img, 20 * math.exp(-t / 0.1))
        return tint(img, (255, 255, 255), math.exp(-t / 0.08))


# ---------- Szene 4: Outro ----------
F_O1, F_O2 = font("Inter-Black.otf", 96), font("Inter-Medium.otf", 34)


def scene_outro(t, dur):
    p = t / dur
    img = fill(COVER_S, 1.35 - 0.2 * ease_io(p), 0.58, 0.42)
    img = tint(img, (0, 0, 0), 0.35 + 0.25 * p)
    img = rgb_split(img, 18 * math.exp(-t / 0.1))
    img = tint(img, (255, 255, 255), math.exp(-t / 0.07))
    d = ImageDraw.Draw(img)
    a = ease_out((t - 0.25) / 0.5)
    if a > 0:
        c = int(255 * a)
        text_center(d, 1480 + 30 * (1 - a), "MICHAEL JACKSON", F_O1, (c, c, c))
        d.rectangle((W / 2 - 60 * a, 1610, W / 2 + 60 * a, 1614), fill=GREEN)
        text_center(d, 1640, "BILLIE JEAN  ·  THRILLER", F_O2, (int(200 * a),) * 3, 6)
    if t > dur - 0.6:
        img = tint(img, (0, 0, 0), (t - (dur - 0.6)) / 0.6)
    return img


# ---------- Zusammenbau ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", help="Videodatei mit dem echten Auftritt")
    ap.add_argument("--start", type=float, default=217.0, help="Startsekunde im Clip (Standard 3:37)")
    ap.add_argument("--dur", type=float, default=5.0, help="Laenge des Ausschnitts")
    ap.add_argument("--out", default=os.path.join(HERE, "mj_edit.mp4"))
    a = ap.parse_args()

    if a.clip:
        clip = Clip(a.clip, a.start, a.dur)
        mid = (clip.scene, len(clip.frames) / FPS)
    else:
        mid = (scene_cuts, BEAT * len(SHOTS))
    scenes = [(scene_intro, BEAT * 4), (scene_player, 4.6), mid, (scene_outro, 2.8)]
    clip_at = scenes[0][1] + scenes[1][1]

    tmp = a.out + ".video.mp4"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    i = 0
    for fn, dur in scenes:
        for k in range(round(dur * FPS)):
            enc.stdin.write(finish(fn(k / FPS, dur), i).tobytes())
            i += 1
    enc.stdin.close()
    enc.wait()

    if a.clip:  # Originalton des Ausschnitts an die richtige Stelle legen
        ms = int(clip_at * 1000)
        r = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", tmp, "-ss", str(a.start), "-t", str(mid[1]), "-i", a.clip,
             "-filter_complex", f"[1:a]afade=t=in:d=0.05,afade=t=out:st={mid[1] - 0.3}:d=0.3,adelay={ms}:all=1[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", a.out])
        if r.returncode == 0:
            os.remove(tmp)
        else:
            os.replace(tmp, a.out)
    else:
        os.replace(tmp, a.out)
    print(f"fertig: {a.out}  ({i / FPS:.1f} s, {i} Bilder)")


if __name__ == "__main__":
    main()
