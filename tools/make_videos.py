#!/usr/bin/env python3
"""Short, silent looping videos for farazisgiannis.com, made from CC0 / public-domain photos of the AVRASTRO photo library
(owner request 11 Oct 2026: "make the site livelier with short videos, from material without copyright").

Each video is a slow "camera" move over a few photos (push in, pull back or pan) joined by soft dissolves, and it loops
without a jump: the last photo dissolves into the first frame. No text is burned in (the page carries the words, in
both languages), no sound. Output per film: <name>.mp4 (H.264, plays everywhere), <name>.webm (VP9, smaller) and
<name>.jpg (the first frame, shown before the video plays and to visitors who prefer less motion).

Usage: python3 tools/make_videos.py <folder with the originals> [name …]
The originals are the full-size CC0 files listed in assets/video/SOURCES.md (vero-os: tools/website/fetch_originals.py
downloads them by Openverse id). Needs Pillow and ffmpeg (libx264, libvpx-vp9).
"""
import json, os, subprocess, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'video')
FPS = 30

# scene: (photo, focus x, focus y, move) — move: 'in' (push in), 'out' (pull back), 'left' / 'right' (pan)
FILMS = {
    # home page: the stages of a life the advisor stays beside ("Μαζί σου, κάθε στιγμή")
    'film-home': {'size': (960, 600), 'hold': 2.6, 'fade': 1.0, 'scenes': [
        ('c4-family', .46, .42, 'in'), ('r-family', .36, .42, 'out'), ('r-health', .42, .45, 'right'),
        ('r-education', .40, .42, 'in'), ('c4-retirement', .72, .52, 'in')]},
    # solutions page: life, health, home, retirement
    'film-solutions': {'size': (960, 640), 'hold': 2.4, 'fade': .9, 'scenes': [
        ('art-whole-life', .50, .42, 'in'), ('q-health', .50, .45, 'left'), ('t-mortgage', .50, .55, 'in'),
        ('t-retirement', .42, .50, 'out')]},
    # how I work: talk, needs, proposal, staying alongside
    'film-how': {'size': (960, 640), 'hold': 2.4, 'fade': .9, 'scenes': [
        ('contact-hero', .50, .50, 'right'), ('q-priorities', .46, .50, 'in'), ('t-score', .60, .42, 'left'),
        ('a-trial', .55, .42, 'in')]},
    # guides: reading and understanding
    'film-guides': {'size': (960, 640), 'hold': 2.6, 'fade': 1.0, 'scenes': [
        ('c-guides', .50, .48, 'in'), ('art-education', .50, .45, 'out'), ('t-checkup', .50, .58, 'in')]},
}


def smooth(a):
    a = max(0.0, min(1.0, a))
    return a * a * (3 - 2 * a)


def crop_box(img, size, fx, fy, move, p):
    """Source rectangle for progress p (0…1) of a scene: zoom 1.00↔1.10 around the focus, or a pan at zoom 1.12."""
    W, H = img.size
    tw, th = size
    base = min(W / tw, H / th)          # largest crop of the output's shape that fits the photo
    if move in ('in', 'out'):
        z = 1.0 + 0.10 * (p if move == 'in' else 1 - p)
        cw, ch = tw * base / z, th * base / z
        # the focus drifts toward the centre of the frame as the camera moves in
        cx = W / 2 + (fx * W - W / 2) * (0.25 + 0.75 * (p if move == 'in' else 1 - p))
        cy = H / 2 + (fy * H - H / 2) * (0.25 + 0.75 * (p if move == 'in' else 1 - p))
    else:
        z = 1.12
        cw, ch = tw * base / z, th * base / z
        span = W - cw
        x0 = (fx * W - cw / 2) - 0.45 * span * (0.5 - p) * (1 if move == 'right' else -1)
        cx = x0 + cw / 2
        cy = fy * H
    cx = min(max(cx, cw / 2), W - cw / 2)
    cy = min(max(cy, ch / 2), H - ch / 2)
    return (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)


def vignette(size):
    w, h = size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((-w * .18, -h * .25, w * 1.18, h * 1.25), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(min(w, h) * .18))
    return m.point(lambda v: int(222 + v * 33 / 255))  # corners at ~87 % brightness


def render(name, spec, src):
    size, hold, fade, scenes = spec['size'], spec['hold'], spec['fade'], spec['scenes']
    photos = {s[0]: Image.open(os.path.join(src, s[0] + '.jpg')).convert('RGB') for s in scenes}
    n = len(scenes)
    step = hold + fade
    T = n * step                       # loop length
    win = hold + 2 * fade              # how long each photo is on screen, dissolves included
    frames = int(round(T * FPS))
    vig = Image.merge('RGB', [vignette(size)] * 3)
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, name)
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{size[0]}x{size[1]}',
                            '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '25', '-pix_fmt', 'yuv420p',
                            '-profile:v', 'high', '-movflags', '+faststart', base + '.mp4'], stdin=subprocess.PIPE)
    first = None
    for f in range(frames):
        t = fade + f / FPS            # start with the first photo fully in, so the first frame (the poster) is a clean picture
        acc = None
        for k, (key, fx, fy, move) in enumerate(scenes):
            u = (t - k * step) % T
            if u >= win: continue
            w = smooth(u / fade) if u < fade else (1 - smooth((u - hold - fade) / fade) if u >= hold + fade else 1.0)
            if w <= 0: continue
            im = photos[key].transform(size, Image.EXTENT, crop_box(photos[key], size, fx, fy, move, u / win), Image.BICUBIC)
            acc = im if acc is None or w >= 1 else Image.blend(acc, im, w) if acc is not None else im
        frame = ImageChops.multiply(acc, vig)
        if first is None: first = frame
        enc.stdin.write(frame.tobytes())
    enc.stdin.close()
    if enc.wait(): raise SystemExit(f'{name}: H.264 encoding failed')
    first.save(base + '.jpg', quality=82, optimize=True, progressive=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.mp4', '-an', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38',
                    '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', base + '.webm'], check=True)
    sizes = {ext: os.path.getsize(base + ext) // 1024 for ext in ('.mp4', '.webm', '.jpg')}
    print(f'{name}: {T:.1f} s loop, {size[0]}x{size[1]}, ' + ', '.join(f'{k} {v} KB' for k, v in sizes.items()))
    return T


def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    src = sys.argv[1]
    names = sys.argv[2:] or list(FILMS)
    for name in names: render(name, FILMS[name], src)


if __name__ == '__main__':
    main()
