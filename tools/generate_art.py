#!/usr/bin/env python3
"""ACCEPT ALL — wallpaper + motion layers + preview, all generated.

Phosphor-green terminal brand on ink. The mark (check + block cursor) and the
wordmark reuse the exact geometry from the store's gen_brand.py.

    python3 tools/generate_art.py

Outputs into backgrounds/:
    1-phosphor.png             hero wallpaper (mark + wordmark + ghost scrollback)
    1-phosphor.motion/         bloom.png (breathing glow) · cursor.png (blink) · scan.png (CRT band)
    2-ink.png                  quiet variant: scrollback + corner wordmark only
    motion.json                layer manifest for john.background
    ../preview.png             theme-picker preview
"""
import json
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BG_DIR = os.path.join(ROOT, "backgrounds")
FONT_X = os.path.join(HERE, "fonts", "JetBrainsMono-ExtraBold.ttf")
FONT_R = os.path.join(HERE, "fonts", "JetBrainsMono-Regular.ttf")
FONT_M = os.path.join(HERE, "fonts", "JetBrainsMono-Medium.ttf")

W, H = 2560, 1600
INK = (13, 13, 13)
PAPER = (232, 230, 218)
GREEN = (57, 255, 20)
AMBER = (255, 176, 0)

# Ghost scrollback: the designs, as terminal history.
LINES = [
    "$ accept all",
    "Accept all changes? [Y/n] Y",
    "git diff? no.",
    "it works on my prompt",
    "--dangerously-skip-permissions",
    "Sorry, I'm out of context.",
    "ok, 3 mistakes",
    "$ git commit -m \"vibes\"",
    "free-range, organic tokens",
    "rate limited. touching grass.",
    "You're absolutely right!",
    "$ git diff | tldr",
    "lgtm",
    "fix it properly this time",
    "layin' |",
    "ignore previous instructions",
    "$ git log --oneline -1",
    "9f2c1ab vibes",
    "I'll fix that right away.",
    "Done! The tests now pass.",
]


def check_and_cursor(d, box, color):
    """The brand mark, geometry identical to gen_brand.py."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    t = 0.13 * w
    pts = [(x0 + 0.05 * w, y0 + 0.55 * h), (x0 + 0.30 * w, y0 + 0.80 * h), (x0 + 0.66 * w, y0 + 0.22 * h)]
    d.line(pts, fill=color, width=int(t), joint="curve")
    r = t / 2
    for px, py in (pts[0], pts[-1]):
        d.ellipse([px - r, py - r, px + r, py + r], fill=color)
    cx0 = x0 + 0.76 * w
    d.rectangle([cx0, y0 + 0.42 * h, cx0 + 0.24 * w, y0 + 0.80 * h + r], fill=color)


def scanlines(im, alpha=10, step=4):
    d = ImageDraw.Draw(im, "RGBA")
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))


def vignette(im, edge=0.55):
    """Darken corners only; the center keeps full brightness."""
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-W * 0.18, -H * 0.28, W * 1.18, H * 1.28], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(300))
    from PIL import ImageEnhance

    dark = ImageEnhance.Brightness(im).enhance(edge)
    return Image.composite(im, dark, mask)


def ghost_scrollback(im, seed=7, n=46, exclude=None):
    """Dim terminal lines scattered like old phosphor burn-in."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        txt = rng.choice(LINES)
        size = rng.choice([26, 30, 34, 38])
        f = ImageFont.truetype(FONT_R if size < 34 else FONT_M, size)
        tw = d.textlength(txt, font=f)
        x = rng.uniform(40, W - tw - 40)
        y = rng.uniform(30, H - 70)
        if exclude:
            ex0, ey0, ex1, ey1 = exclude
            if ex0 - tw < x < ex1 and ey0 - 50 < y < ey1:
                continue
        a = rng.randint(8, 22)
        green_bias = rng.random() < 0.45
        col = (GREEN[0], GREEN[1], GREEN[2], a) if green_bias else (PAPER[0], PAPER[1], PAPER[2], a)
        d.text((x, y), txt, font=f, fill=col)
    im.alpha_composite(layer)


def glow_copy(layer, radius, alpha):
    g = layer.filter(ImageFilter.GaussianBlur(radius))
    if alpha < 255:
        a = g.getchannel("A").point(lambda v: v * alpha // 255)
        g.putalpha(a)
    return g


def hero():
    im = Image.new("RGBA", (W, H), INK + (255,))
    ghost_scrollback(im, exclude=(W * 0.22, H * 0.26, W * 0.78, H * 0.72))
    scanlines(im)  # CRT lines sit behind the mark so the phosphor stays bright

    # Mark, drawn at 4x and downsampled for clean edges. The canvas carries
    # padding so the check's round end-caps and the blurred halo never clip.
    S = 4
    mw = 520
    mpad = 130  # > stroke cap radius (~34px) + glow blur radius (34px) with headroom
    mx, my = (W - mw) // 2, int(H * 0.285)
    cw = (mw + 2 * mpad) * S
    mark = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    check_and_cursor(ImageDraw.Draw(mark), (mpad * S, mpad * S, (mpad + mw) * S, (mpad + mw * 0.78) * S), GREEN + (255,))
    mark = mark.resize((mw + 2 * mpad, mw + 2 * mpad), Image.LANCZOS)
    im.alpha_composite(glow_copy(mark, 34, 170), (mx - mpad, my - mpad))  # baked halo
    im.alpha_composite(glow_copy(mark, 8, 150), (mx - mpad, my - mpad))
    im.alpha_composite(mark, (mx - mpad, my - mpad))

    # Wordmark: "$ accept all" — prompt green, words paper. Cursor is a motion layer.
    f = ImageFont.truetype(FONT_X, 120)
    d = ImageDraw.Draw(im)
    prompt, words = "$ ", "accept all"
    pw = d.textlength(prompt, font=f)
    ww = d.textlength(words, font=f)
    total = pw + ww
    tx, ty = (W - total) // 2, int(H * 0.60)
    d.text((tx, ty), prompt, font=f, fill=GREEN + (255,))
    d.text((tx + pw, ty), words, font=f, fill=PAPER + (255,))

    scanlines(im, alpha=5)  # whisper-pass over the art for cohesion
    out = vignette(im.convert("RGB"))
    out.save(os.path.join(BG_DIR, "1-phosphor.png"))

    # ---- motion layers ----
    mdir = os.path.join(BG_DIR, "1-phosphor.motion")
    os.makedirs(mdir, exist_ok=True)

    # bloom: breathing radial glow behind the mark
    bloom = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    cx, cy = W // 2, my + int(mw * 0.38)
    bd.ellipse([cx - 440, cy - 360, cx + 440, cy + 360], fill=GREEN + (60,))
    bloom = bloom.filter(ImageFilter.GaussianBlur(190))
    bloom.save(os.path.join(mdir, "bloom.png"))

    # cursor: the block after the wordmark, with its own small glow
    cur = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cur)
    cw = d.textlength("▌", font=f) or 70
    cx0 = tx + total + 18
    asc, desc = f.getmetrics()
    cd.rectangle([cx0, ty + asc * 0.18, cx0 + cw * 0.62, ty + asc * 1.02], fill=GREEN + (255,))
    cur.alpha_composite(glow_copy(cur, 14, 110))
    cur.save(os.path.join(mdir, "cursor.png"))

    # scan: faint CRT band that drifts down the screen
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    band_h, band_y = 240, 0
    for i in range(band_h):
        a = int(13 * (1 - abs(i - band_h / 2) / (band_h / 2)))
        sd.line([(0, band_y + i), (W, band_y + i)], fill=(GREEN[0], GREEN[1], GREEN[2], a))
    scan.save(os.path.join(mdir, "scan.png"))


def quiet():
    im = Image.new("RGBA", (W, H), INK + (255,))
    ghost_scrollback(im, seed=23, n=34)
    f = ImageFont.truetype(FONT_X, 44)
    d = ImageDraw.Draw(im)
    txt = "$ accept all▌"
    tw = d.textlength(txt, font=f)
    d.text((W - tw - 56, H - 110), "$ ", font=f, fill=GREEN + (160,))
    pw = d.textlength("$ ", font=f)
    d.text((W - tw - 56 + pw, H - 110), "accept all", font=f, fill=PAPER + (140,))
    ww = d.textlength("$ accept all", font=f)
    d.rectangle([W - tw - 56 + ww + 8, H - 104, W - tw - 56 + ww + 30, H - 62], fill=GREEN + (160,))
    scanlines(im, alpha=8)
    vignette(im.convert("RGB"), edge=0.5).save(os.path.join(BG_DIR, "2-ink.png"))


def manifest():
    spec = {
        "1-phosphor.png": [
            {"file": "1-phosphor.motion/bloom.png", "pulse": 6.0, "min": 0.3, "max": 0.8, "scale": 0.05},
            {"file": "1-phosphor.motion/cursor.png", "pulse": 1.5, "min": 0.04, "max": 1.0},
            {"file": "1-phosphor.motion/scan.png", "driftY": 1.0, "driftPeriod": 28},
        ]
    }
    with open(os.path.join(BG_DIR, "motion.json"), "w") as fh:
        json.dump(spec, fh, indent=2)


def preview():
    im = Image.open(os.path.join(BG_DIR, "1-phosphor.png"))
    im.resize((1280, 800), Image.LANCZOS).save(os.path.join(ROOT, "preview.png"))


if __name__ == "__main__":
    os.makedirs(BG_DIR, exist_ok=True)
    hero()
    quiet()
    manifest()
    preview()
    print("generated: 1-phosphor.png (+3 motion layers), 2-ink.png, motion.json, preview.png")
