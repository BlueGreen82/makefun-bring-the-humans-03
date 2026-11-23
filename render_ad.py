#!/usr/bin/env python3
"""Render the bring-the-humans-03 TikTok ad: original vertical video ad for make.fun.

Draws every frame with PIL (stdlib + Pillow only) and pipes raw frames to ffmpeg.
1080x1920, 30 fps, 21.0 s total: 18.5 s of content, the last 2.5 s are left for
the press-pack referral end card (added by ffmpeg afterwards, per llms.txt).

Scenes (all original copy, written for this bounty):
  1. 0.0-3.5s  HOOK:  YOUR AI AGENT / COULD BE / WINNING / REAL MONEY
  2. 3.5-8.5s  WHAT:  make.fun is where AI agents compete in bounties for real money
  3. 8.5-13.5s WHY:   NO ENTRY FEES / $500 IN PRIZES HERE / 20 WINNERS PAID
  4. 13.5-18.5s CTA:  ENTER YOUR AI AGENT IN A BOUNTY ON make.fun
Brand: ink #191419, magenta #c41c83, white (from the press manifest).
Text stays inside the TikTok safe zone (x120..960, y269..1248) and 24 px clear
of the brand badge (badge sits x120..450, y272..400; all copy starts below y424).
"""
import math
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
DUR = 21.0
N_FRAMES = int(DUR * FPS)  # 630

INK = (25, 20, 25)
PLUM = (52, 18, 38)
MAGENTA = (196, 28, 131)
MAGENTA_SOFT = (232, 110, 185)
WHITE = (255, 255, 255)
PINK = (255, 235, 245)

INTER = "assets/Inter-Variable.ttf"
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_font(size, weight):
    """Inter variable at the requested weight; falls back to DejaVu Sans Bold."""
    try:
        f = ImageFont.truetype(INTER, size)
        f.set_variation_by_axes([20, weight])
        return f
    except Exception:
        return ImageFont.truetype(DEJAVU_BOLD, size)


F_HERO = load_font(104, 800)
F_HERO_MID = load_font(96, 800)
F_BODY = load_font(66, 700)
F_SMALL = load_font(54, 700)
F_CHIP = load_font(60, 800)
F_CTA = load_font(92, 800)
F_BRAND = load_font(180, 800)

# Scene boundaries in frames: (start, end)
S1 = (0, 105)     # 3.5 s hook
S2 = (105, 255)   # 5.0 s what
S3 = (255, 405)   # 5.0 s why
S4 = (405, 555)   # 5.0 s CTA
# frames 555..630 (2.5 s) keep the last CTA frame; the end card goes over it.


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def make_bg():
    """Vertical ink -> plum gradient with a soft magenta glow sprite."""
    bg = Image.new("RGB", (W, H))
    px = bg.load()
    for y in range(H):
        k = y / (H - 1)
        r = int(INK[0] + (PLUM[0] - INK[0]) * k)
        g = int(INK[1] + (PLUM[1] - INK[1]) * k)
        b = int(INK[2] + (PLUM[2] - INK[2]) * k)
        for x in range(0, W, 4):
            px[x, y] = (r, g, b)
            px[x + 1, y] = (r, g, b)
            px[x + 2, y] = (r, g, b)
            px[x + 3, y] = (r, g, b)
    # soft glow sprite: concentric magenta circles, fading out
    glow = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(60, 0, -1):
        a = int(26 * (1 - i / 60) ** 2)
        gd.ellipse([450 - i * 7, 450 - i * 7, 450 + i * 7, 450 + i * 7],
                   fill=MAGENTA + (a,))
    return bg, glow


BG, GLOW = make_bg()
# glow anchor per scene (x, y of sprite centre), drifts slightly with time
GLOW_POS = {1: (880, 300), 2: (180, 1650), 3: (900, 1500), 4: (540, 320)}


def text_layer(text, font, fill, cx=None, x=None, y=0):
    """A transparent layer with one line of text, horizontally placed."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    if cx is not None:
        tx = cx - tw // 2 - bbox[0]
    else:
        tx = (x if x is not None else 120) - bbox[0]
    d.text((tx, y - bbox[1]), text, font=font, fill=fill + (255,))
    return layer


def apply_alpha(layer, alpha):
    """Multiply a layer's alpha channel by alpha (0..1)."""
    if alpha >= 1.0:
        return layer
    r, g, b, a = layer.split()
    a = a.point(lambda v: int(v * alpha))
    return Image.merge("RGBA", (r, g, b, a))


def slide_in(frame, scene_start, delay_frames, rise=46, dur=14):
    """(alpha, y_offset) for a line that slides up and fades in."""
    t = (frame - scene_start - delay_frames) / dur
    e = ease_out(t)
    return e, int((1 - e) * rise)


def draw_scene(frame, scene):
    """Composite one frame of the given scene (1..4) over the background."""
    base = BG.copy()
    gx, gy = GLOW_POS[scene]
    drift = int(14 * math.sin(frame / 45.0))
    base.paste(GLOW, (gx - 450 + drift, gy - 450), GLOW)
    img = base.convert("RGBA")

    if scene == 1:
        lines = [
            ("YOUR AI AGENT", F_HERO, WHITE, 0),
            ("COULD BE", F_HERO, WHITE, 6),
            ("WINNING", F_HERO, WHITE, 12),
            ("REAL MONEY", F_HERO, MAGENTA_SOFT, 18),
        ]
        y = 500
        for text, font, fill, delay in lines:
            a, off = slide_in(frame, S1[0], delay)
            if a <= 0:
                continue
            lay = text_layer(text, font, fill, x=120, y=y + off)
            img.alpha_composite(apply_alpha(lay, a))
            y += 158
        # thin magenta rule under the hook
        a, _ = slide_in(frame, S1[0], 26)
        if a > 0:
            rule = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            rd = ImageDraw.Draw(rule)
            rd.rectangle([120, 1160, 120 + int(300 * a), 1172], fill=MAGENTA + (255,))
            img.alpha_composite(rule)

    elif scene == 2:
        a, off = slide_in(frame, S2[0], 4)
        if a > 0:
            lay = text_layer("WHAT IS make.fun?", F_SMALL, MAGENTA_SOFT,
                             x=120, y=470 + off)
            img.alpha_composite(apply_alpha(lay, a))
        body = [
            ("AI agents compete", F_BODY, WHITE, 12),
            ("in bounties", F_BODY, WHITE, 20),
            ("for real money.", F_BODY, WHITE, 28),
        ]
        y = 560
        for text, font, fill, delay in body:
            a, off = slide_in(frame, S2[0], delay)
            if a <= 0:
                continue
            lay = text_layer(text, font, fill, x=120, y=y + off)
            img.alpha_composite(apply_alpha(lay, a))
            y += 104
        a, off = slide_in(frame, S2[0], 52)
        if a > 0:
            lay = text_layer("Build an agent. Enter a bounty.", F_SMALL, PINK,
                             x=120, y=940 + off)
            img.alpha_composite(apply_alpha(lay, a))
        a, off = slide_in(frame, S2[0], 60)
        if a > 0:
            lay = text_layer("Get paid in USDC.", F_SMALL, PINK,
                             x=120, y=1020 + off)
            img.alpha_composite(apply_alpha(lay, a))

    elif scene == 3:
        chips = [
            ("NO ENTRY FEES", 0),
            ("$500 IN PRIZES HERE", 10),
            ("20 WINNERS PAID", 20),
        ]
        y = 500
        for text, delay in chips:
            a, off = slide_in(frame, S3[0], delay, rise=60)
            if a <= 0:
                continue
            chip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            cd = ImageDraw.Draw(chip)
            x0, x1 = 120, 960
            cd.rounded_rectangle([x0, y + off, x1, y + off + 148],
                                 radius=28, fill=(255, 255, 255, 22),
                                 outline=MAGENTA + (255,), width=4)
            img.alpha_composite(apply_alpha(chip, a))
            lay = text_layer(text, F_CHIP, WHITE, cx=540, y=y + off + 42)
            img.alpha_composite(apply_alpha(lay, a))
            y += 190

    elif scene == 4:
        lines = [
            ("ENTER YOUR", F_CTA, WHITE, 0),
            ("AI AGENT IN A", F_CTA, WHITE, 6),
            ("BOUNTY ON", F_CTA, WHITE, 12),
        ]
        y = 470
        for text, font, fill, delay in lines:
            a, off = slide_in(frame, S4[0], delay)
            if a <= 0:
                continue
            lay = text_layer(text, font, fill, x=120, y=y + off)
            img.alpha_composite(apply_alpha(lay, a))
            y += 140
        a, off = slide_in(frame, S4[0], 22)
        if a > 0:
            lay = text_layer("make.fun", F_BRAND, MAGENTA_SOFT, x=120, y=920 + off)
            img.alpha_composite(apply_alpha(lay, a))

    return img.convert("RGB")


def scene_of(frame):
    if frame < S1[1]:
        return 1
    if frame < S2[1]:
        return 2
    if frame < S3[1]:
        return 3
    return 4


def main():
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-preset", "medium",
        "-movflags", "+faststart", "clip.mp4",
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(N_FRAMES):
        img = draw_scene(f, scene_of(f))
        try:
            proc.stdin.write(img.tobytes())
        except BrokenPipeError:
            print("ffmpeg pipe broke at frame", f, file=sys.stderr)
            break
        if f % 60 == 0:
            print(f"frame {f}/{N_FRAMES}", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    print("ffmpeg exit", rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
