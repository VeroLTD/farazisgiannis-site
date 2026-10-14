#!/usr/bin/env python3
"""Renders the free checklists (tools/checklists.py) to A4 PDFs in assets/pdf/ (ideas track 7, 14 Oct 2026).
Uses Playwright's Chromium offline (Node; found with `npm root -g`, or PLAYWRIGHT_DIR) and the site's own fonts
(assets/fonts, Commissioner as static instances made with fontTools; Russian falls back to the system sans-serif, as Commissioner has no Cyrillic). The PDFs are committed;
build.py only copies them. Run after changing the texts: python3 tools/make_pdfs.py
"""
import html, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checklists import CHECKLISTS, FOOT, pdf_name

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'pdf')
esc = lambda s: html.escape(s, quote=True)

CSS = '''
@font-face { font-family: "GFS Didot"; src: url("FONTS/GFSDidot-Regular.woff") format("woff"); }
@font-face { font-family: "Commissioner"; src: url("STATIC/Commissioner-400.ttf") format("truetype"); font-weight: 400; }
@font-face { font-family: "Commissioner"; src: url("STATIC/Commissioner-600.ttf") format("truetype"); font-weight: 600; }
@page { size: A4; margin: 16mm 16mm 18mm; }
* { box-sizing: border-box; }
body { margin: 0; font: 400 10.6pt/1.5 "Commissioner", "DejaVu Sans", sans-serif; color: #18202b; }
header { display: flex; align-items: center; justify-content: space-between; gap: 8mm; background: #142a4c; color: #e6edf6; border-radius: 4mm; padding: 6mm 7mm; }
header img { height: 15mm; }
header .who { text-align: right; font-size: 9pt; color: #c3cfdf; }
header .who b { display: block; color: #c9a35f; font-weight: 600; font-size: 10pt; }
h1 { font: 400 25pt/1.1 "GFS Didot", "DejaVu Serif", serif; color: #142a4c; margin: 8mm 0 2mm; }
.lead { font-size: 11.5pt; color: #4a5568; margin: 0 0 3mm; }
.intro { border-left: 1mm solid #c9a35f; padding: 1mm 0 1mm 4mm; margin: 0 0 4mm; color: #18202b; }
h2 { font: 400 15pt/1.2 "GFS Didot", "DejaVu Serif", serif; color: #142a4c; margin: 6mm 0 2mm; break-after: avoid; }
ul { list-style: none; padding: 0; margin: 0; }
li { display: grid; grid-template-columns: 6mm 1fr; gap: 2.5mm; padding: 1.6mm 0; border-bottom: .25mm solid #d9e1eb; break-inside: avoid; }
li::before { content: ""; width: 4mm; height: 4mm; border: .35mm solid #142a4c; border-radius: .8mm; margin-top: .9mm; }
.close { margin-top: 6mm; background: #edf2f8; border-radius: 3mm; padding: 4mm 5mm; break-inside: avoid; }
footer { margin-top: 6mm; font-size: 8.5pt; color: #4a5568; border-top: .3mm solid #c9a35f; padding-top: 2.5mm; }
'''

def page(c, lang):
    _, _, title, desc, intro, sections, close = c
    who = {'el': ('Γιάννης Φαραζής', 'Ασφαλιστικός Σύμβουλος'), 'en': ('Giannis Farazis', 'Insurance Advisor'), 'ru': ('Яннис Фаразис', 'Страховой консультант')}[lang]
    body = ''.join(f'<h2>{esc(t[lang])}</h2><ul>' + ''.join(f'<li><span>{esc(x[lang])}</span></li>' for x in items) + '</ul>' for t, items in sections)
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{esc(title[lang])}</title><style>{CSS}</style></head><body>'
            f'<header><img src="IMG/gf-lockup.png" alt=""><div class="who"><b>{who[0]}</b>{who[1]}<br>+357 97 840941</div></header>'
            f'<h1>{esc(title[lang])}</h1><p class="lead">{esc(desc[lang])}</p><p class="intro">{esc(intro[lang])}</p>{body}'
            f'<p class="close">{esc(close[lang])}</p><footer>{esc(FOOT[lang])}</footer></body></html>')

RENDER = r'''
const path = require('path'), fs = require('fs');
const { chromium } = require(process.env.PW);
(async () => {
  const dir = process.argv[2], out = process.argv[3];
  const b = await chromium.launch();
  const page = await b.newPage();
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.html')).sort()) {
    await page.goto('file://' + path.join(dir, f), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(out, f.replace(/\.html$/, '.pdf')), format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="width:100%;font-size:7pt;color:#8a94a6;text-align:right;padding-right:16mm"><span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
    console.log('pdf', f);
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
'''

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
        for c in CHECKLISTS:
            for lang in ('el', 'en', 'ru'):
                doc = page(c, lang).replace('FONTS/', 'file://' + fonts + '/').replace('IMG/', 'file://' + img + '/').replace('STATIC/', 'file://' + tmp + '/')
                open(os.path.join(tmp, pdf_name(c[1], lang).replace('.pdf', '.html')), 'w', encoding='utf-8').write(doc)
        js = os.path.join(tmp, 'render.cjs'); open(js, 'w').write(RENDER)
        subprocess.run(['node', js, tmp, OUT], check=True, env={**os.environ, 'PW': pw})
    print('PDFs in', OUT)

if __name__ == '__main__':
    main()
