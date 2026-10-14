#!/usr/bin/env python3
"""Social-preview cards (og:image), one per page and language: assets/img/og/<page>-<lang>.jpg (1200 x 630).

Owner's rule of 14 Oct 2026: no photograph twice on the site, also not as a preview image. So the cards carry no photo at
all: the page's own title in the site's typography on the site's colours, with the monogram's line-work. Pre-built and
committed like the PDFs; run after changing a page title:  PREVIEW=1 python3 tools/make_og.py   (Pillow + fontTools)
"""
import io, os, re, sys, html, unicodedata
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault('PREVIEW', '1')
import build  # noqa: E402

OUT = os.path.join(ROOT, 'assets', 'img', 'og')
W, H = 1200, 630
MID, MID2, LAPEL, BRASS, SOFT = (20, 42, 76), (15, 34, 64), (29, 58, 102), (201, 163, 95), (231, 211, 168)

def font(name, size, weight=400):
    f = TTFont(os.path.join(ROOT, 'assets', 'fonts', name)); f.flavor = None
    b = io.BytesIO(); f.save(b); b.seek(0)
    cmap = set(f.getBestCmap())
    ft = ImageFont.truetype(b, size)
    if 'fvar' in f and name.startswith('Commissioner'):
        ft.set_variation_by_axes([weight] + [0] * (len(f['fvar'].axes) - 1) if len(f['fvar'].axes) > 1 else [weight])
    return ft, cmap

def chain(*items):
    return [font(*x) for x in items]

def pick(fonts, ch):
    for f, cmap in fonts:
        if ord(ch) in cmap or ch == ' ': return f
    return fonts[0][0]

def width(fonts, text):
    return sum(pick(fonts, c).getlength(c) for c in text)

def draw_text(d, xy, text, fonts, fill):
    x, y = xy
    for c in text:
        f = pick(fonts, c); d.text((x, y), c, font=f, fill=fill); x += f.getlength(c)

def wrap(fonts, text, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if width(fonts, t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def card(title, kicker, path):
    im = Image.new('RGB', (W, H), MID)
    # soft light from the top right, as in the page headers
    glow = Image.new('L', (W, H), 0); g = ImageDraw.Draw(glow)
    for r in range(700, 0, -20): g.ellipse((W - 200 - r, -260 - r * .6, W - 200 + r, -260 + r * .6 + 400), fill=int(70 * (1 - r / 700)))
    im = Image.composite(Image.new('RGB', (W, H), LAPEL), im, glow)
    d = ImageDraw.Draw(im)
    # the monogram's line-work (the LINES drawing of the site, scaled)
    s, ox, oy = 1.25, 760, 70
    P = lambda x, y: (ox + x * s, oy + y * s)
    lw = 3
    for a, b in [((330, 92), (150, 92)), ((215, 92), (55, 252)), ((330, 190), (180, 190)), ((180, 190), (40, 330)), ((220, 190), (80, 330)), ((262, 214), (168, 308)), ((330, 40), (190, 40))]:
        d.line([P(*a), P(*b)], fill=BRASS, width=lw)
    d.arc([P(40, 40)[0], P(40, 40)[1], P(340, 340)[0], P(340, 340)[1]], 180, 270, fill=BRASS, width=lw)
    d.arc([P(-30, 40)[0], P(-30, 40)[1], P(330, 400)[0], P(330, 400)[1]], 0, 90, fill=BRASS, width=lw)
    d.rectangle((0, H - 10, W, H), fill=BRASS)
    disp = chain(('GFSDidot-Regular.woff', 66), ('FGDisplayCyr.woff', 60), ('Commissioner-var.woff', 60))
    small = chain(('Commissioner-var.woff', 26, 600), ('Inter-Cyrillic-600.woff', 25))
    foot = chain(('Commissioner-var.woff', 24, 420), ('Inter-Cyrillic-400.woff', 23))
    draw_text(d, (72, 78), (unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', kicker.upper()) if unicodedata.category(c) != 'Mn')) if re.search('[α-ω]', kicker) else kicker.upper()), small, BRASS)
    lines = wrap(disp, title, 700)[:4]
    y = 150 if len(lines) > 2 else 190
    for ln in lines:
        draw_text(d, (72, y), ln, disp, (255, 255, 255)); y += 80
    draw_text(d, (72, H - 86), 'farazisgiannis.com  ·  +357 97 840941', foot, (201, 213, 228))
    im.save(path, 'JPEG', quality=86, optimize=True, progressive=True)

def main():
    os.makedirs(OUT, exist_ok=True)
    made = 0
    for pid, fn in build.PAGES.items():
        for lang in build.LANGS:
            if lang == 'ru':
                build.RENDER['ru'] = True
                try: doc = build.ru_page(fn('en'))
                finally: build.RENDER['ru'] = False
            else:
                doc = fn(lang)
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', doc, re.S)
            title = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else 'Giannis Farazis'
            if pid == 'home':
                title = {'el': 'Προστασία, αποταμίευση και ηρεμία', 'en': 'Protection, savings and peace of mind', 'ru': 'Защита, накопления и спокойствие'}[lang]
            kicker = {'el': 'Γιάννης Φαραζής · Ασφαλιστικός Σύμβουλος', 'en': 'Giannis Farazis · Insurance Advisor', 'ru': 'Яннис Фаразис · страховой консультант'}[lang]
            card(title, kicker, os.path.join(OUT, f'{pid}-{lang}.jpg')); made += 1
    print('og cards:', made)

if __name__ == '__main__':
    main()
