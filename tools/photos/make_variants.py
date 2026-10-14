#!/usr/bin/env python3
"""Makes the photos the site serves, from tools/photos/manifest.json:

  assets/img/photos/<slot>-<width>.avif and .webp   (3:2, widths from the manifest that the source can fill)
  assets/img/photos/photos.json                     (read by build.py: sizes, alt texts in el/en/ru, credits)
  assets/img/photos/CREDITS.md                       (who took each photo, where it comes from, the licence)

Source of a slot: tools/photos/fetched/<slot>.jpg when the workflow downloaded one (and the slot has no photo of its own
or says "replace"), otherwise tools/photos/src/<slot>.*. A slot with neither is left out (the page then shows no photo).
Needs Pillow with AVIF (python3 -m pip install pillow). Run: python3 tools/photos/make_variants.py
"""
import glob, json, os, sys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'assets', 'img', 'photos')
RATIO = 3 / 2

def source(key, slot, fetched):
    f = os.path.join(HERE, 'fetched', key + '.jpg')
    own = sorted(glob.glob(os.path.join(HERE, 'src', key + '.*')))
    if os.path.exists(f) and key in fetched and (not own or slot.get('fetch', {}).get('replace')):
        return f, fetched[key], slot['fetch'].get('alt', slot['alt']), True
    if own:
        return own[0], slot.get('credit', {}), slot['alt'], False
    return None, None, None, False

def crop32(im):
    im = ImageOps.exif_transpose(im).convert('RGB')
    w, h = im.size
    if w / h > RATIO:
        nw = round(h * RATIO); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = round(w / RATIO); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
    return im

def main():
    man = json.load(open(os.path.join(HERE, 'manifest.json'), encoding='utf-8'))
    fpath = os.path.join(HERE, 'fetched', 'fetched.json')
    fetched = json.load(open(fpath, encoding='utf-8')) if os.path.exists(fpath) else {}
    os.makedirs(OUT, exist_ok=True)
    made, index = set(), {}
    for key, slot in man['slots'].items():
        src, cred, alt, was_fetched = source(key, slot, fetched)
        if not src:
            continue
        im = crop32(Image.open(src))
        widths = [w for w in man['widths'] if w <= im.width]
        if not widths or im.width - widths[-1] >= 120: widths.append(im.width)   # e.g. a 900 px source: 480 and 900
        for w in widths:
            v = im.resize((w, round(w / RATIO)), Image.LANCZOS) if w != im.width else im
            for ext, kw in (('avif', {'quality': 52, 'speed': 4}), ('webp', {'quality': 78, 'method': 6})):
                name = f'{key}-{w}.{ext}'
                v.save(os.path.join(OUT, name), ext.upper(), **kw)
                made.add(name)
        index[key] = {'page': slot['page'], 'use': slot['use'], 'widths': widths, 'alt': alt, 'credit': cred, 'fetched': was_fetched}
    for f in os.listdir(OUT):   # photos no longer in the manifest (the repeats of the 14 Oct 2026 audit) go
        if f not in made and f not in ('photos.json', 'CREDITS.md'):
            os.remove(os.path.join(OUT, f))
    with open(os.path.join(OUT, 'photos.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1); f.write('\n')
    rows = ['# Photo credits', '',
            'Every photograph is used once on the whole site (owner, 14 Oct 2026). CC0 1.0 / Public Domain unless the row says',
            'otherwise (Pixabay Content License for photos the workflow downloaded from Pixabay). Made by tools/photos/make_variants.py',
            'from tools/photos/manifest.json.', '',
            '| Photo | Page | Where | Shows | Title | Photographer | Source | Licence |', '|---|---|---|---|---|---|---|---|']
    for key, v in index.items():
        c = v['credit'] or {}
        rows.append(f"| {key} | {v['page']} | {v['use']} | {v['alt']['en']} | {c.get('title') or '—'} | {c.get('creator') or '—'} | "
                    f"{('[' + c['page'].split('/')[2] + '](' + c['page'] + ')') if c.get('page') else '—'} | {c.get('license', '—')} |")
    pending = [k for k in man['slots'] if k not in index or (man['slots'][k].get('fetch', {}).get('replace') and not index[k]['fetched'])]
    if pending:
        rows += ['', 'Waiting for the workflow «Site photos» (.github/workflows/photos.yml): ' + ', '.join(pending) + '.']
    with open(os.path.join(OUT, 'CREDITS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    total = sum(os.path.getsize(os.path.join(OUT, n)) for n in made)
    print(f'photos: {len(index)} slots, {len(made)} files, {total // 1024} KB; pending: {", ".join(pending) or "none"}')

if __name__ == '__main__':
    sys.exit(main())
