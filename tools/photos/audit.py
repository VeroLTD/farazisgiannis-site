#!/usr/bin/env python3
"""Photo audit (owner's rule of 14 Oct 2026: no photograph twice on the site, not even in another crop).

Compares a 64-bit difference hash (dHash, robust to resizing and mild re-compression) of every served photo
(assets/img/photos/*-480.webp) with every other one, and with the "reserved" fingerprints in the manifest: the
photographs inside the short films (assets/video/SOURCES.md), the films' first frames and the explainer posters.

  python3 tools/photos/audit.py                       check (exit 1 on a repeat)
  python3 tools/photos/audit.py --reserve <dir>...    (re)compute the reserved fingerprints from image files, e.g. the
                                                      AVRASTRO library photos the films were made from
Needs Pillow. check.py (no dependencies) checks the other half: each slot is used on one page only.
"""
import glob, json, os, sys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LIMIT = 12   # Hamming distance at or below which two images count as the same photograph

def dhash(path, crop_center=True):
    im = ImageOps.exif_transpose(Image.open(path)).convert('L')
    if crop_center:   # compare the 3:2 centre, as the site crops it
        w, h = im.size
        if w / h > 1.5: nw = int(h * 1.5); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(w / 1.5); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize((9, 8), Image.LANCZOS)
    px = list(im.tobytes())
    bits = ''.join('1' if px[r * 9 + c] > px[r * 9 + c + 1] else '0' for r in range(8) for c in range(8))
    return f'{int(bits, 2):016x}'

def dist(a, b): return bin(int(a, 16) ^ int(b, 16)).count('1')

def main(argv):
    mpath = os.path.join(HERE, 'manifest.json')
    man = json.load(open(mpath, encoding='utf-8'))
    if argv[:1] == ['--reserve']:
        res = {}
        for item in argv[1:]:
            files = [item] if os.path.isfile(item) else sorted(glob.glob(os.path.join(item, '*.*')))
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    res[os.path.relpath(f, ROOT) if f.startswith(ROOT) else os.path.basename(f)] = dhash(f)
        man['reserved'] = res
        with open(mpath, 'w', encoding='utf-8') as fh:
            json.dump(man, fh, ensure_ascii=False, indent=1); fh.write('\n')
        print('reserved fingerprints:', len(res)); return 0
    served = {os.path.basename(f)[:-len('-480.webp')]: dhash(f) for f in sorted(glob.glob(os.path.join(ROOT, 'assets/img/photos/*-480.webp')))}
    problems = []
    keys = list(served)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if dist(served[a], served[b]) <= LIMIT: problems.append(f'{a} looks like {b} ({dist(served[a], served[b])})')
        for name, h in man.get('reserved', {}).items():
            if dist(served[a], h) <= LIMIT: problems.append(f'{a} looks like {name} ({dist(served[a], h)}), which is in a film or poster')
    print('\n'.join(problems) or f'photo audit: {len(served)} photos, each one unique (checked against {len(man.get("reserved", {}))} film/poster images)')
    return 1 if problems else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
