"""Build the Thar vs Escape Velocity animatic: frames + VO + synthesised sound design.

Notes:
  * The Devanagari face available here has no OpenType shaping, so Hindi subtitles
    are transliterated to Latin script (fonts lack raqm/HarfBuzz). Hinglish reads
    fine for this genre anyway.
  * All SFX are synthesised with numpy (no external samples) — the silence in
    shot 04 is deliberate.
"""

import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
SB = os.path.join(HERE, "storyboard")
AUD = os.path.join(HERE, "audio")
TMP = "/tmp/build"
W, H, FPS, DUR = 1600, 900, 30, 60.0
SR = 44100
N = int(SR * DUR)

os.makedirs(TMP, exist_ok=True)

INK = (17, 17, 17)
RED = (179, 20, 30)
CREAM = (245, 242, 238)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# --------------------------------------------------------------------------- audio
def silence():
    return np.zeros(N, dtype=np.float32)


def t_axis(dur):
    return np.arange(int(SR * dur), dtype=np.float32) / SR


def add(buf, sig, at):
    i = int(at * SR)
    j = min(N, i + len(sig))
    if i < N:
        buf[i:j] += sig[: j - i]


def place(buf, wav_path, at):
    with wave.open(wav_path, "rb") as w:
        assert w.getnchannels() == 1 and w.getframerate() == SR
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    add(buf, data, at)
    return len(data) / SR


def env(dur, a=0.01, d=0.1, s=0.7, r=0.2):
    n = int(SR * dur)
    e = np.ones(n, dtype=np.float32) * s
    na, nr = int(SR * a), int(SR * r)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def expdecay(dur, tau):
    return np.exp(-t_axis(dur) / tau).astype(np.float32)


def lowpass(x, cutoff):
    """One-pole low-pass, cutoff in Hz."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.copy(x)
    # vectorised approximation via cumulative filtering is unstable; loop is fine here
    prev = 0.0
    out = np.empty_like(x)
    for i in range(len(x)):
        prev = (1 - a) * x[i] + a * prev
        out[i] = prev
    return out


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def sweep(f0, f1, dur, kind="sine", curve=2.0):
    t = t_axis(dur)
    u = (t / dur) ** (1.0 / curve)
    f = f0 + (f1 - f0) * u
    phase = 2 * np.pi * np.cumsum(f) / SR
    if kind == "sine":
        return np.sin(phase).astype(np.float32)
    if kind == "saw":
        return (2 * ((phase / (2 * np.pi)) % 1.0) - 1).astype(np.float32)
    if kind == "square":
        return np.sign(np.sin(phase)).astype(np.float32)
    raise ValueError(kind)


def noise(dur):
    return np.random.uniform(-1, 1, int(SR * dur)).astype(np.float32)


# --- individual SFX ---------------------------------------------------------
def sfx_sub_boom():
    d = 2.6
    body = sweep(95, 28, d, "sine", curve=1.6) * expdecay(d, 0.55)
    thud = lowpass(noise(d), 180) * expdecay(d, 0.10) * 2.2
    return (body * 0.95 + thud).astype(np.float32)


def sfx_impact():
    d = 1.2
    crack = highpass(noise(d), 900) * expdecay(d, 0.05)
    body = sweep(140, 40, d, "sine", 1.5) * expdecay(d, 0.22)
    return (crack * 0.55 + body * 0.8).astype(np.float32)


def sfx_drop_whoosh():
    d = 0.9
    n = lowpass(highpass(noise(d), 300), 3500)
    sweep_env = np.linspace(0.15, 1.0, len(n)) ** 2
    return (n * sweep_env * 0.55).astype(np.float32)


def sfx_scratch():
    d = 0.42
    base = sweep(1100, 120, d, "saw", 1.2)
    grit = highpass(noise(d), 1800) * 0.6
    e = expdecay(d, 0.12)
    return ((base * 0.5 + grit) * e).astype(np.float32)


def sfx_ting():
    d = 2.2
    f = 1568.0
    s = np.zeros(int(SR * d), dtype=np.float32)
    for i, (mult, amp) in enumerate([(1, 1.0), (2.01, 0.45), (3.02, 0.22), (4.5, 0.1)]):
        s += amp * np.sin(2 * np.pi * f * mult * t_axis(d)) * expdecay(d, 0.5 / (i + 1))
    return s * 0.35


def sfx_rev():
    d = 2.4
    t = t_axis(d)
    f = 55 + 210 * (t / d) ** 1.3
    phase = 2 * np.pi * np.cumsum(f) / SR
    rumble = (2 * ((phase / (2 * np.pi)) % 1) - 1) * 0.55
    rumble = lowpass(rumble, 900)
    grit = lowpass(noise(d), 700) * 0.35
    e = env(d, 0.05, 0.1, 1.0, 0.35)
    return ((rumble + grit) * e * 0.75).astype(np.float32)


def sfx_jet():
    d = 2.6
    roar = lowpass(noise(d), 1400) * 0.9
    whine = sweep(420, 2600, d, "sine", 1.4) * 0.22
    e = env(d, 0.25, 0.2, 1.0, 0.5)
    return ((roar + whine) * e * 0.8).astype(np.float32)


def sfx_sonic_boom():
    d = 3.3
    bang = highpass(noise(d), 120) * expdecay(d, 0.18) * 1.5
    ring = sweep(180, 30, d, "sine", 1.2) * expdecay(d, 0.9)
    return (bang * 0.75 + ring * 0.9).astype(np.float32)


def sfx_cricket():
    """One awkward chirp: ~4 pulses around 4.5 kHz."""
    d = 0.8
    out = np.zeros(int(SR * d), dtype=np.float32)
    for k in range(4):
        start = 0.06 + k * 0.13
        n = int(SR * 0.05)
        t = np.arange(n) / SR
        chirp = np.sin(2 * np.pi * (4600 + 300 * k) * t + 6 * np.sin(2 * np.pi * 70 * t))
        chirp *= np.hanning(n)
        i = int(start * SR)
        out[i:i + n] += chirp.astype(np.float32) * 0.35
    return out


def sfx_wind():
    d = DUR
    n = lowpass(noise(d), 420) * 0.10
    lfo = 0.65 + 0.35 * np.sin(2 * np.pi * 0.08 * t_axis(d))
    return (n * lfo).astype(np.float32)


def sfx_riser(dur):
    t = t_axis(dur)
    f = 120 * (1 + 12 * (t / dur) ** 2)
    phase = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(phase) * 0.28
    air = lowpass(noise(dur), 5000) * np.linspace(0, 0.4, len(t))
    return ((tone + air) * np.linspace(0.15, 1.0, len(t)) ** 2).astype(np.float32)


def sfx_pad(dur, freqs=(110, 164.81, 220, 329.63), amp=0.16):
    t = t_axis(dur)
    s = np.zeros(len(t), dtype=np.float32)
    for i, f in enumerate(freqs):
        s += np.sin(2 * np.pi * f * t + i) * (amp / (i + 1))
    e = env(dur, min(1.2, dur / 3), 0.3, 0.85, min(1.5, dur / 2.5))
    return (s * e).astype(np.float32)


def sfx_heart():
    d = 0.5
    a = sweep(70, 40, 0.16, "sine", 1.2) * expdecay(0.16, 0.06)
    b = sweep(64, 36, 0.16, "sine", 1.2) * expdecay(0.16, 0.06) * 0.7
    out = np.zeros(int(SR * d), dtype=np.float32)
    out[int(0.02 * SR):int(0.02 * SR) + len(a)] += a
    out[int(0.24 * SR):int(0.24 * SR) + len(b)] += b
    return out * 0.9


def phonk(dur):
    """Half-time phonk-ish bed at 72 BPM: 808, cowbell, kick, snare, hat."""
    beat = 60 / 72.0
    total = int(SR * dur)
    out = np.zeros(total, dtype=np.float32)

    def put(sig, at, gain=1.0):
        i = int(at * SR)
        j = min(total, i + len(sig))
        if i < total:
            out[i:j] += sig[: j - i] * gain

    # 808 line (A minor-ish)
    pattern = [(0, 55.0, 1.0), (1.5, 65.41, 0.9), (2.0, 55.0, 0.85), (3.0, 49.0, 1.0),
               (4.0, 55.0, 0.9), (5.5, 73.42, 0.85), (6.0, 65.41, 0.95), (7.0, 55.0, 1.0)]
    for bar in range(int(np.ceil(dur / (beat * 8))) + 1):
        for pos, f, g in pattern:
            at = bar * beat * 8 + pos * beat
            if at > dur:
                continue
            d = beat * 1.05
            sig = np.sin(2 * np.pi * f * t_axis(d) + 0.6 * np.sin(2 * np.pi * 2 * f * t_axis(d)))
            sig *= expdecay(d, beat * 0.55) * g * 0.55
            put(sig.astype(np.float32), at)

    # kick on 1 and 3, snare on 3, hats on 8ths
    for k in np.arange(0, dur, beat):
        kick = sweep(160, 44, 0.32, "sine", 1.3) * expdecay(0.32, 0.09) * 0.75
        put(kick.astype(np.float32), k)
        hat = highpass(noise(0.05), 6000) * expdecay(0.05, 0.012) * 0.22
        put(hat.astype(np.float32), k + beat / 2)
        hat2 = highpass(noise(0.04), 7000) * expdecay(0.04, 0.010) * 0.14
        put(hat2.astype(np.float32), k)
    for k in np.arange(beat, dur, beat * 2):
        snare = (highpass(noise(0.22), 900) * expdecay(0.22, 0.06) * 0.5).astype(np.float32)
        body = (sweep(220, 150, 0.12, "sine", 1.1) * expdecay(0.12, 0.04) * 0.3).astype(np.float32)
        snare[:len(body)] += body
        put(snare, k)

    # cowbell melody, sparse
    for k in np.arange(0, dur, beat * 2):
        f = 587.33
        cl = (np.sin(2 * np.pi * f * t_axis(0.18)) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t_axis(0.18)))
        cl *= expdecay(0.18, 0.055) * 0.16
        put(cl.astype(np.float32), k + beat * 0.5)
    return out


# --------------------------------------------------------------------------- picture
CROPS = {"12_drift_into_void.png": (0.0, 0.0, 1.0, 0.84)}


def load(name):
    """Load a storyboard frame, preferring the full-res master, cropping letterbox bars."""
    base = os.path.splitext(name)[0]
    for cand in (os.path.join(SB, name), os.path.join(SB, "web", base + ".jpg")):
        if os.path.exists(cand):
            im = Image.open(cand).convert("RGB")
            break
    else:
        raise FileNotFoundError(name)
    # crop baked-in letterbox bars (near-black rows at top/bottom)
    g = im.convert("L")
    w, h = g.size
    rows = [g.crop((0, y, w, y + 1)).resize((1, 1)).getpixel((0, 0)) for y in range(h)]
    top = 0
    while top < h // 4 and rows[top] < 12:
        top += 1
    bot = h
    while bot > h * 3 // 4 and rows[bot - 1] < 12:
        bot -= 1
    if top or bot < h:
        im = im.crop((0, top, w, bot))
    if name in CROPS:
        x0, y0, x1, y1 = CROPS[name]
        w2, h2 = im.size
        im = im.crop((int(w2 * x0), int(h2 * y0), int(w2 * x1), int(h2 * y1)))
    return im


def plate_bg(im):
    """Background for letterbox padding: flat colour when the frame border is uniform
    (white void), otherwise a blurred, darkened cover-crop of the frame itself."""
    w, h = im.size
    border = [im.getpixel((x, 0)) for x in range(0, w, 11)]
    border += [im.getpixel((x, h - 1)) for x in range(0, w, 11)]
    border += [im.getpixel((0, y)) for y in range(0, h, 11)]
    border += [im.getpixel((w - 1, y)) for y in range(0, h, 11)]
    arr = np.array(border, dtype=np.float32)
    med = np.median(arr, axis=0)
    if float(np.mean(arr.std(axis=0))) < 20:
        return ("flat", tuple(int(c) for c in med))
    # cover-crop + blur
    s = max(W / w, H / h)
    r = im.resize((int(w * s) + 2, int(h * s) + 2), Image.LANCZOS)
    x = (r.width - W) // 2
    y = (r.height - H) // 2
    r = r.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(48))
    r = Image.eval(r, lambda v: int(v * 0.72))
    return ("blur", r)


def cover(im, scale, dx=0.5, dy=0.5, bg=None):
    """Fit the frame into the 16:9 canvas at `scale` (1.0 = fit), padding with a
    background derived from the frame, so the manga composition keeps its negative space."""
    iw, ih = im.size
    s = min(W / iw, H / ih) * scale
    nw, nh = max(1, int(iw * s)), max(1, int(ih * s))
    r = im.resize((nw, nh), Image.LANCZOS)
    if scale > 1.0:
        r = r.filter(ImageFilter.UnsharpMask(radius=1.3, percent=40, threshold=2))
    kind, b = bg if bg is not None else plate_bg(im)
    if kind == "blur" and scale <= 1.02:
        canvas = b.copy()
    else:
        canvas = Image.new("RGB", (W, H), b if kind == "flat" else (0, 0, 0))
        if kind == "blur":
            canvas = b.copy()
    x = int((W - nw) * dx)
    y = int((H - nh) * dy)
    canvas.paste(r, (x, y))
    return canvas


def white_card():
    return Image.new("RGB", (W, H), (250, 250, 250))


def black_card():
    return Image.new("RGB", (W, H), (0, 0, 0))


F_TITLE = font(BOLD, 118)
F_TITLE_S = font(BOLD, 62)
F_KICK = font(MONO, 30)
F_SUB = font(BOLD, 54)
F_SMALL = font(MONO, 26)


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def subtitle_card(text, speaker=None):
    """Caption bar baked into the frame, manga-style."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fnt = F_SUB if len(text) < 70 else font(BOLD, 44)
    lines = wrap(d, text, fnt, int(W * 0.78))
    pad = 34
    lh = fnt.size + 16
    block_h = lh * len(lines) + pad * 2
    y0 = H - block_h - 70
    # measure widest line
    widest = max(d.textlength(l, font=fnt) for l in lines)
    x0 = int((W - widest) / 2 - pad)
    x1 = int((W + widest) / 2 + pad)
    d.rectangle([x0, y0, x1, y0 + block_h], fill=(10, 10, 10, 225))
    d.rectangle([x0, y0, x0 + 10, y0 + block_h], fill=RED + (255,))
    y = y0 + pad
    for l in lines:
        lw = d.textlength(l, font=fnt)
        d.text(((W - lw) / 2, y), l, font=fnt, fill=(255, 255, 255, 255))
        y += lh
    if speaker:
        fname = font(MONO, 22)
        tw = d.textlength(speaker, font=fname)
        d.rectangle([x0 + 26, y0 - 34, x0 + 26 + tw + 26, y0 - 2], fill=RED + (255,))
        d.text((x0 + 39, y0 - 31), speaker, font=fname, fill=(255, 255, 255, 255))
    return im


def overlay_text(base, text, speaker=None):
    im = base.convert("RGBA")
    im.alpha_composite(subtitle_card(text, speaker))
    return im.convert("RGB")


def speed_lines(im, strength=0.0, color=INK):
    """Horizontal manga speed lines, drawn once and cached per strength bucket."""
    if strength <= 0:
        return im
    rng = np.random.default_rng(7)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    n = int(60 + 220 * strength)
    for _ in range(n):
        y = int(rng.integers(0, H))
        x0 = int(rng.integers(-200, W))
        ln = int(rng.integers(180, 900))
        a = int(40 + 120 * strength * rng.random())
        th = int(rng.integers(2, 7))
        d.line([x0, y, x0 + ln, y], fill=color + (a,), width=th)
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    out = im.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def flash(im, amount):
    if amount <= 0:
        return im
    w = Image.new("RGB", (W, H), (255, 255, 255))
    return Image.blend(im, w, min(1.0, amount))


# --------------------------------------------------------------------------- timeline
def build_frames(start=0, end=None):
    os.makedirs(os.path.join(TMP, "frames"), exist_ok=True)
    total = int(FPS * DUR)
    end = total if end is None else min(end, total)

    # load plates once
    P = {n: load(n) for n in [
        "01_setup_kneeling.png", "02_thar_drop.png", "03_eyes_snap.png",
        "04_point_to_sky.png", "05_cockpit_speedo.png", "06_speedbreaker_launch.png",
        "07_sonic_boom.png", "08_zero_gravity.png", "09_sweat_drop.png",
        "10_facepalm.png", "11_giant_hand.png", "12_drift_into_void.png"]}

    # beat -> (plate, start, duration, zoom_start, zoom_end, pan) 
    beats = [
        ("01_setup_kneeling.png", 0.0, 4.6, 1.02, 1.10, (0.5, 0.45)),
        ("02_thar_drop.png", 4.6, 3.2, 1.16, 1.02, (0.5, 0.5)),
        ("02_thar_drop.png", 7.8, 2.2, 1.02, 1.12, (0.48, 0.52)),
        ("03_eyes_snap.png", 10.0, 3.6, 1.03, 1.16, (0.5, 0.45)),
        ("04_point_to_sky.png", 13.6, 4.4, 1.12, 1.03, (0.5, 0.5)),
        ("05_cockpit_speedo.png", 18.0, 3.4, 1.05, 1.20, (0.5, 0.5)),
        ("06_speedbreaker_launch.png", 21.4, 3.1, 1.18, 1.02, (0.5, 0.45)),
        ("07_sonic_boom.png", 24.5, 3.5, 1.02, 1.14, (0.5, 0.5)),
        ("08_zero_gravity.png", 28.0, 6.0, 1.02, 1.13, (0.45, 0.5)),
        ("09_sweat_drop.png", 34.0, 6.0, 1.06, 1.20, (0.5, 0.45)),
        ("10_facepalm.png", 40.0, 5.0, 1.14, 1.02, (0.5, 0.5)),
        ("11_giant_hand.png", 45.0, 6.0, 1.02, 1.12, (0.5, 0.4)),
        ("12_drift_into_void.png", 51.0, 7.0, 1.04, 1.16, (0.5, 0.55)),
    ]

    subs = [
        (1.0, 4.4, "Hey Bhagwan, ek lambi, ek Thar de do…", None),
        (11.2, 13.4, "Thank you Prabhu! Par isme aisi speed do ki dharti pe mujhe koi pakad na paye! Ekdum Rocket!", "JIRA"),
        (19.6, 21.2, "Ab aayega na asli mazaa. Let's gooo!", "JIRA"),
        (30.6, 39.4, "Arey bhai bhai bhai! Highway pe nikalna tha, sidha orbit mein phek diya!", "JIRA"),
        (44.0, 48.6, "Escape velocity de di. Physics ne aukaat dikha di.", "JIRA"),
        (52.2, 59.4, "Vats, ab orbit mein hi ghoomo… aur haan, jaate-jaate baaki bachchon ko bolna Sansi Sir ko zaroor follow karein!", "BHAGWAN"),
    ]

    # pre-build caption overlays (they're expensive)
    cap_cache = {}
    line_cache = {}

    title_card = white_card()
    d = ImageDraw.Draw(title_card)
    d.text((120, 300), "THAR", font=font(BOLD, 150), fill=INK)
    d.text((120, 440), "vs", font=font(BOLD, 96), fill=RED)
    d.text((120, 560), "ESCAPE VELOCITY", font=font(BOLD, 104), fill=INK)
    d.text((124, 700), "ANIME / MANGA EDITION", font=F_KICK, fill=RED)
    d.line([120, 690, 760, 690], fill=RED, width=6)

    end_card = black_card()
    d = ImageDraw.Draw(end_card)
    d.text((120, 430), "PHYSICS: 1", font=font(BOLD, 92), fill=(255, 255, 255))
    d.text((120, 540), "JIRA: 0", font=font(BOLD, 92), fill=RED)
    d.text((124, 700), "SANSI SIR KO ZAROOR FOLLOW KAREIN", font=F_KICK, fill=(235, 235, 235))

    for fi in range(start, end):
        t = fi / FPS
        # pick beat
        beat = None
        for b in beats:
            if b[1] <= t < b[1] + b[2]:
                beat = b
                break
        if t < 0.9:
            im = title_card
        elif t < 1.6:
            a = (t - 0.9) / 0.7
            im = Image.blend(title_card, cover(P["01_setup_kneeling.png"], 1.02, 0.5, 0.45), a)
        elif t >= 59.62:
            im = end_card
        elif beat is None:
            im = cover(P["12_drift_into_void.png"], 1.16, 0.5, 0.55)
        else:
            plate, start, dur, z0, z1, pan = beat
            u = (t - start) / dur
            z = z0 + (z1 - z0) * u
            im = cover(P[plate], z, pan[0], pan[1])

            # impact punch-in on the Thar drop
            if plate == "02_thar_drop.png" and 0 <= t - 4.6 < 0.16:
                k = (t - 4.6) / 0.16
                im = cover(P[plate], 1.16 + 0.07 * (1 - k), 0.5, 0.5)
                im = flash(im, 0.55 * (1 - k))
            # speed lines: demand + launch
            if plate in ("03_eyes_snap.png", "04_point_to_sky.png") and t >= 10.6:
                s = 0.5 + 0.2 * np.sin(t * 9)
                key = f"sl{int(s*10)}"
                if key not in line_cache:
                    line_cache[key] = speed_lines(im, s)
                im = line_cache[key]
            if plate == "06_speedbreaker_launch.png":
                key = "sl_launch"
                if key not in line_cache:
                    line_cache[key] = speed_lines(im, 0.85)
                im = line_cache[key]
                if t - 21.4 < 0.12:
                    im = flash(im, 0.5 * (1 - (t - 21.4) / 0.12))
            if plate == "07_sonic_boom.png" and t - 24.5 < 0.14:
                im = flash(im, 0.7 * (1 - (t - 24.5) / 0.14))

        # vignette on caption frames only when a caption is up
        cap = None
        for c0, c1, txt, who in subs:
            if c0 <= t <= c1:
                cap = (txt, who)
                break
        if cap:
            key = cap
            if key not in cap_cache:
                cap_cache[key] = subtitle_card(cap[0], cap[1])
            base = im.convert("RGBA")
            base.alpha_composite(cap_cache[key])
            im = base.convert("RGB")

        im.save(os.path.join(TMP, "frames", f"f{fi:05d}.jpg"), quality=90, subsampling=1)
        if fi % 150 == 0:
            print(f"frame {fi}/{total}")


def build_audio():
    mix = silence()

    # ambient bed early (white void hum), then space wind
    hum = sfx_pad(10.0, (55, 82.4, 110), 0.05)
    add(mix, hum, 0.0)

    # 0:01.0 song-style devotional pad under the prayer
    add(mix, sfx_pad(3.6, (196, 261.6, 329.6, 392), 0.07), 1.0)
    add(mix, sfx_rev() * 0.18, 2.6)

    # VO 1 — prayer
    place(mix, os.path.join(TMP, "01_jira_prayer.wav"), 1.2)

    # 0:04.6 the drop
    add(mix, sfx_drop_whoosh(), 3.9)
    add(mix, sfx_impact(), 4.6)
    add(mix, sfx_sub_boom() * 1.15, 4.62)

    # 0:10.0 record scratch, then VO 2
    add(mix, sfx_scratch(), 10.05)
    place(mix, os.path.join(TMP, "02_jira_demand.wav"), 10.9)
    add(mix, sfx_riser(1.2) * 0.5, 12.8)

    # 0:18.0 cockpit: ting + rev, then launch
    add(mix, sfx_ting() * 0.9, 18.1)
    add(mix, sfx_rev(), 19.0)
    add(mix, sfx_riser(2.2) * 0.45, 19.2)
    place(mix, os.path.join(TMP, "03_jira_launch_scream.wav"), 19.6)
    add(mix, sfx_jet() * 0.85, 21.4)
    add(mix, sfx_sonic_boom(), 24.4)

    # 0:28.0 — hard silence. Only space wind and one cricket chirp.
    add(mix, sfx_wind() * 0.5, 30.0)
    add(mix, sfx_heart() * 0.42, 29.5)
    add(mix, sfx_cricket(), 30.2)
    place(mix, os.path.join(TMP, "04_jira_zero_g.wav"), 30.6)
    add(mix, sfx_heart() * 0.4, 36.0)

    # 0:40.0 phonk drops (shot 05), carries through to the end
    ph = phonk(20.0)
    add(mix, ph * 0.85, 40.0)
    place(mix, os.path.join(TMP, "05_jira_realization.wav"), 44.0)

    # 0:45 giant hand: low swell under the beat
    add(mix, sfx_sub_boom() * 0.6, 45.0)
    add(mix, sfx_pad(7.0, (73.4, 110, 146.8), 0.09), 45.0)

    # 0:52.2 Bhagwan
    add(mix, sfx_pad(7.0, (110, 164.8, 220, 277.2), 0.10), 52.0)
    place(mix, os.path.join(TMP, "06_bhagwan_booming.wav"), 52.2)

    # final sub hit + tail at 59.2
    add(mix, sfx_sub_boom() * 0.8, 59.2)
    add(mix, sfx_ting() * 0.25, 59.4)

    # gentle master: remove DC, soft clip, normalise to -1 dBFS peak
    mix = mix - np.mean(mix)
    peak = np.max(np.abs(mix))
    mix = mix / max(peak, 1e-6) * 0.89
    mix = np.tanh(mix * 1.15) * 0.92
    mix = mix / max(np.max(np.abs(mix)), 1e-6) * 0.95

    out = os.path.join(TMP, "mix.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("audio ->", out)
    return out


def main():
    print("building audio…")
    mix = build_audio()
    print("building frames…")
    build_frames()
    video = os.path.join(HERE, "Thar_vs_Escape_Velocity_Animatic.mp4")
    cmd = [FF, "-y", "-loglevel", "error",
           "-framerate", str(FPS), "-i", os.path.join(TMP, "frames", "f%05d.jpg"),
           "-i", mix,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", video]
    print("encoding…")
    subprocess.run(cmd, check=True)
    print("saved", video, os.path.getsize(video) // (1024 * 1024), "MB")


if __name__ == "__main__":
    main()
