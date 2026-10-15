#!/usr/bin/env python3
"""Renders the free checklists (tools/checklists.py) to A4 PDFs in assets/pdf/ (ideas track 7, 14 Oct 2026; premium
design 15 Oct 2026 — owner: everything printed or downloaded must look made with absolute care).

Layout: the GF lockup and "free checklist" on a light first-page header with a brass rule; the title in GFS Didot; the
sections numbered 01, 02… with tick boxes; the closing note; and at the end a signature block with his details (name,
life-insurance capacity and ICCS registration, mobile, office line, office address, website; no insurer, no e-mail)
beside the QR code of the Guides page in the PDF's language. Every page carries "Giannis Farazis · farazisgiannis.com"
and "n / N" in its margins (CSS @page margin boxes).

Uses Playwright's Chromium offline (Node; found with `npm root -g`, or PLAYWRIGHT_DIR; CHROMIUM may name the browser)
and the site's own fonts (assets/fonts: Commissioner as static instances made with fontTools; Russian letters from the
Cyrillic-only FG Display Cyr and Inter files, as on the site). The PDFs are committed; build.py only copies them.
Run after changing the texts: python3 tools/make_pdfs.py
"""
import html, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checklists import CHECKLISTS, FOOT, pdf_name
import qr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'pdf')
esc = lambda s: html.escape(s, quote=True)

CSS = '''
@font-face { font-family: "GFS Didot"; src: url("FONTS/GFSDidot-Regular.woff") format("woff"); }
@font-face { font-family: "GFS Didot"; src: url("STATIC/FGDisplayCyr.ttf") format("truetype"); unicode-range: U+0400-045F, U+0490-0491, U+2116; }
@font-face { font-family: "Commissioner"; src: url("STATIC/Commissioner-400.ttf") format("truetype"); font-weight: 400; }
@font-face { font-family: "Commissioner"; src: url("STATIC/Commissioner-600.ttf") format("truetype"); font-weight: 600; }
@font-face { font-family: "Commissioner"; src: url("STATIC/Inter-Cyrillic-400.ttf") format("truetype"); font-weight: 400; unicode-range: U+0400-045F, U+0490-0491, U+2116; }
@font-face { font-family: "Commissioner"; src: url("STATIC/Inter-Cyrillic-600.ttf") format("truetype"); font-weight: 600; unicode-range: U+0400-045F, U+0490-0491, U+2116; }
@page {
  size: A4; margin: 15mm 17mm 17mm;
  @bottom-left { content: "Giannis Farazis · farazisgiannis.com"; font: 400 7pt/1 "Commissioner", sans-serif; color: #7d8898; letter-spacing: .04em; vertical-align: top; padding-top: 6mm; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 600 7pt/1 "Commissioner", sans-serif; color: #7d8898; letter-spacing: .06em; vertical-align: top; padding-top: 6mm; }
}
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 400 9.8pt/1.5 "Commissioner", "DejaVu Sans", sans-serif; color: #18202b; }
.head { display: flex; align-items: flex-end; justify-content: space-between; gap: 10mm; padding: 0 0 4.5mm; border-bottom: .8pt solid #c9a35f; }
.head img { display: block; height: 12.5mm; }
.head .meta { text-align: right; font-size: 7.4pt; line-height: 1.55; color: #4a5568; }
.head .meta p { margin: 0; }
.head .kicker { font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: #8a6a2f; margin-bottom: 1mm; }
h1 { font: 400 25pt/1.1 "GFS Didot", "DejaVu Serif", serif; color: #142a4c; margin: 9mm 0 2.4mm; letter-spacing: -.005em; }
.lead { font-size: 11pt; color: #4a5568; margin: 0 0 5mm; max-width: 150mm; }
.intro { margin: 0 0 6mm; padding: 3.4mm 4.5mm; background: #f6f8fb; border-left: 1.6pt solid #c9a35f; border-radius: 0 2mm 2mm 0; color: #2b3442; font-size: 9.4pt; }
section { margin: 0 0 4.5mm; }
h2 { display: flex; align-items: baseline; gap: 3mm; font: 400 14pt/1.2 "GFS Didot", "DejaVu Serif", serif; color: #142a4c; margin: 0 0 1.6mm; padding-bottom: 1.6mm; border-bottom: .8pt solid #c9a35f; break-after: avoid; }
h2 .n { font: 600 7.4pt/1 "Commissioner", sans-serif; letter-spacing: .14em; color: #8a6a2f; }
ul { list-style: none; padding: 0; margin: 0; }
li { display: grid; grid-template-columns: 6.5mm 1fr; gap: 1.5mm; padding: 1.55mm 0; border-bottom: .4pt solid #e3e8ef; break-inside: avoid; }
li::before { content: ""; width: 3.6mm; height: 3.6mm; border: .6pt solid #142a4c; border-radius: .7mm; margin-top: .55mm; }
.close { margin: 6mm 0 0; padding: 4mm 5mm; background: #142a4c; color: #e6edf6; border-radius: 2.4mm; break-inside: avoid; font-size: 9.6pt; border-bottom: 1.4pt solid #c9a35f; }
.foot { margin: 9mm 0 0; padding: 6mm 0 0; border-top: .8pt solid #c9a35f; break-inside: avoid; }
.foot .row { display: flex; justify-content: space-between; gap: 10mm; align-items: stretch; }
.sign { display: flex; gap: 5mm; align-items: flex-start; }
.sign img { width: 15mm; margin-top: .6mm; }
.name { margin: 0; font: 400 16pt/1.15 "GFS Didot", serif; color: #142a4c; }
.role { margin: 1mm 0 3mm; font-size: 8.6pt; color: #4a5568; }
.contact { display: grid; gap: 1mm; }
.contact p { margin: 0; display: grid; grid-template-columns: 20mm 1fr; align-items: baseline; font-size: 8.6pt; }
.contact span { font-size: 6.4pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: #8a94a6; }
.qr { width: 34mm; text-align: center; flex: none; }
.qr svg { display: block; width: 23mm; height: 23mm; margin: 0 auto; }
.qr p { margin: 1.4mm 0 0; font-size: 6.4pt; line-height: 1.4; color: #4a5568; }
.note { margin: 5mm 0 0; font-size: 7.2pt; color: #4a5568; }
.notes { margin: 7mm 0 0; break-inside: avoid; }
.notes .line { height: 8.5mm; border-bottom: .4pt solid #d3dae4; }
'''

T = {
    'kicker': {'el': 'Δωρεάν λίστα ελέγχου', 'en': 'Free checklist', 'ru': 'Бесплатный чек-лист'},
    'name': {'el': 'Γιάννης Φαραζής', 'en': 'Giannis Farazis', 'ru': 'Яннис Фаразис'},
    'role': {'el': 'Ασφαλιστικός Σύμβουλος κλάδου ζωής · Αρ. Μητρώου ΥΕΑΕ 7854', 'en': 'Life insurance advisor · ICCS Reg. No. 7854',
             'ru': 'Консультант по страхованию жизни · рег. № ICCS 7854'},
    'rows': {'el': [('Κινητό', '+357 97 840941'), ('Γραφείο', '+357 22 124867'), ('Διεύθυνση', 'Λεωφόρος Στροβόλου 124Γ, 5ος όροφος, Λευκωσία'), ('Ιστότοπος', 'farazisgiannis.com')],
             'en': [('Mobile', '+357 97 840941'), ('Office', '+357 22 124867'), ('Address', '124C Strovolou Avenue, 5th floor, Nicosia'), ('Website', 'farazisgiannis.com')],
             'ru': [('Мобильный', '+357 97 840941'), ('Офис', '+357 22 124867'), ('Адрес', 'проспект Строволу 124C, 5-й этаж, Никосия'), ('Сайт', 'farazisgiannis.com')]},
    'notes': {'el': 'Σημειώσεις', 'en': 'Notes', 'ru': 'Заметки'},
    'scan': {'el': 'Σαρώστε για όλους τους οδηγούς', 'en': 'Scan for all the guides', 'ru': 'Отсканируйте, чтобы открыть все гиды'},
    # the Guides page in each language (build.py SLUGS 'guides'); the Russian edition is not public yet (build.py
    # RU_LIVE = False), so the Russian PDF points to the English page — change it to /ru/guides/ when Russian goes live
    'guides': {'el': 'https://farazisgiannis.com/odigoi/', 'en': 'https://farazisgiannis.com/en/guides/', 'ru': 'https://farazisgiannis.com/en/guides/'},
}

def qr_svg(url):
    s = qr.svg(qr.encode(url)).replace('fill="#000"', 'fill="#142a4c"')
    return s.split('>', 1)[0].split(' width=')[0] + '>' + s.split('>', 1)[1]

def page(c, lang):
    _, _, title, desc, intro, sections, close = c
    body = ''.join(f'<section><h2><span class="n">{i:02d}</span>{esc(t[lang])}</h2><ul>' + ''.join(f'<li><span>{esc(x[lang])}</span></li>' for x in items) + '</ul></section>'
                   for i, (t, items) in enumerate(sections, 1))
    rows = ''.join(f'<p><span>{esc(k)}</span>{esc(v)}</p>' for k, v in T['rows'][lang])
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{esc(title[lang])} — Giannis Farazis</title><style>{CSS}</style></head><body>'
            f'<div class="head"><img src="IMG/gf-lockup.png" alt="Giannis Farazis"><div class="meta"><p class="kicker">{T["kicker"][lang]}</p><p>farazisgiannis.com</p></div></div>'
            f'<h1>{esc(title[lang])}</h1><p class="lead">{esc(desc[lang])}</p><p class="intro">{esc(intro[lang])}</p>{body}'
            f'<p class="close">{esc(close[lang])}</p>'
            # room to write: the checklist is made to be printed and filled in
            f'<section class="notes"><h2>{T["notes"][lang]}</h2>' + '<div class="line"></div>' * 7 + '</section>'
            f'<div class="foot"><div class="row"><div class="sign"><img src="IMG/gf-mark.png" alt=""><div><p class="name">{T["name"][lang]}</p>'
            f'<p class="role">{T["role"][lang]}</p><div class="contact">{rows}</div></div></div>'
            f'<div class="qr">{qr_svg(T["guides"][lang])}<p>{T["scan"][lang]}</p></div></div><p class="note">{esc(FOOT[lang])}</p></div>'
            '</body></html>')

RENDER = r'''
const path = require('path'), fs = require('fs');
const { chromium } = require(process.env.PW);
(async () => {
  const dir = process.argv[2], out = process.argv[3];
  const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const page = await b.newPage();
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.html')).sort()) {
    await page.goto('file://' + path.join(dir, f), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(out, f.replace(/\.html$/, '.pdf')), format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log('pdf', f);
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
'''

def cff_to_glyf(font):
    """a CFF (PostScript-outline) font converted in place to TrueType outlines (fontTools cu2qu), so Chromium embeds it as
    a real TrueType font in the PDF"""
    from fontTools.ttLib import newTable
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    if 'CFF ' not in font: return
    order = font.getGlyphOrder(); gs = font.getGlyphSet()
    glyf = newTable('glyf'); glyf.glyphOrder = order; glyf.glyphs = {}
    for name in order:
        pen = TTGlyphPen(gs); gs[name].draw(Cu2QuPen(pen, 1.0, reverse_direction=True)); glyf[name] = pen.glyph()
    font['glyf'] = glyf; font['loca'] = newTable('loca')
    maxp = newTable('maxp'); maxp.tableVersion = 0x00010000
    for k in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs', 'maxInstructionDefs', 'maxStackElements', 'maxSizeOfInstructions', 'maxComponentElements'):
        setattr(maxp, k, 0)
    maxp.maxZones = 1; maxp.numGlyphs = len(order); font['maxp'] = maxp
    font['head'].glyphDataFormat = 0; font['post'].formatType = 2.0; font['post'].extraNames = []; font['post'].mapping = {}
    for t in ('CFF ', 'VORG'):
        if t in font: del font[t]
    font.sfntVersion = '\000\001\000\000'

def main():
    pw = os.environ.get('PLAYWRIGHT_DIR') or os.path.join(subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip(), 'playwright')
    if not os.path.isdir(pw):
        sys.exit(f'Playwright not found at {pw}; the PDFs in assets/pdf/ were left as they are.')
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        fonts = os.path.join(ROOT, 'assets', 'fonts'); img = os.path.join(ROOT, 'assets', 'img')
        # Chromium prints a variable font as a thin Type 3 font: static instances of Commissioner for print (fontTools)
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
        for w in (400, 600):
            f = TTFont(os.path.join(fonts, 'Commissioner-var.woff')); f.flavor = None
            instantiateVariableFont(f, {a.axisTag: (w if a.axisTag == 'wght' else a.defaultValue) for a in f['fvar'].axes}, inplace=True)
            f.save(os.path.join(tmp, f'Commissioner-{w}.ttf'))
        # the Cyrillic files too: FG Display Cyr is variable and Inter is CFF, both of which Chromium would embed as Type 3
        f = TTFont(os.path.join(fonts, 'FGDisplayCyr.woff')); f.flavor = None
        if 'fvar' in f: instantiateVariableFont(f, {a.axisTag: (400 if a.axisTag == 'wght' else a.defaultValue) for a in f['fvar'].axes}, inplace=True)
        f.save(os.path.join(tmp, 'FGDisplayCyr.ttf'))
        for w in (400, 600):
            f = TTFont(os.path.join(fonts, f'Inter-Cyrillic-{w}.woff')); f.flavor = None
            cff_to_glyf(f); f.save(os.path.join(tmp, f'Inter-Cyrillic-{w}.ttf'))
        for c in CHECKLISTS:
            for lang in ('el', 'en', 'ru'):
                doc = page(c, lang).replace('FONTS/', 'file://' + fonts + '/').replace('IMG/', 'file://' + img + '/').replace('STATIC/', 'file://' + tmp + '/')
                open(os.path.join(tmp, pdf_name(c[1], lang).replace('.pdf', '.html')), 'w', encoding='utf-8').write(doc)
        js = os.path.join(tmp, 'render.cjs'); open(js, 'w').write(RENDER)
        subprocess.run(['node', js, tmp, OUT], check=True, env={**os.environ, 'PW': pw})
    print('PDFs in', OUT)

if __name__ == '__main__':
    main()
