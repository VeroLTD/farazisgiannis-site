# farazisgiannis.com

Personal website of Giannis Farazis, Insurance Advisor (Nicosia, Cyprus). Greek at `/`, English at `/en/`.

- `build.py` builds the static site into `site/` (no dependencies): `python3 build.py`; `python3 check.py` checks it.
- Content rules (owner's brief of 10 Oct 2026): insurance work only; career since 2024; only the professional mobile
  +357 97 840941 and the office line +357 22 124867; Eurolife only in the contact section; no e-mail address published.
- The contact form posts to `https://app.avrastro.com/v1/enquiry` (the owner's own server in the EU), which e-mails it
  and stores nothing. No cookies, analytics or third-party scripts/fonts.
- Published by `.github/workflows/pages.yml` (GitHub Pages) at https://farazisgiannis.com since 10 Oct 2026. DNS at
  Design.com: A @ → 185.199.108–111.153, CNAME www → veroltd.github.io (TXT _dmarc kept). `site-prefix.txt` is empty;
  putting a path in it (e.g. `/farazisgiannis-site`) builds a non-indexed preview under that path instead.
- Fonts: GFS Didot and Commissioner (SIL Open Font License, files in `assets/fonts`). Portrait: the owner's own photo.
- Videos (11 Oct 2026): four short silent loops in `assets/video` (home page band, and the headers of Solutions, How I
  work and Guides), made by `tools/make_videos.py` from CC0 photos (`assets/video/SOURCES.md`). `assets/js/site.js`
  plays them only while on screen, never with "reduce motion" or Save-Data, and each has a pause button. To remake
  them: download the originals with vero-os `tools/website/fetch_originals.py`, then
  `python3 tools/make_videos.py <folder>` (Pillow + ffmpeg).
- Photos (owner's rule of 14 Oct 2026: every photo matches its topic and appears on ONE page only, also not in another
  crop or inside a film/poster): `tools/photos/manifest.json` (made by `tools/photos/write_manifest.py`) lists every
  slot; `tools/photos/make_variants.py` makes AVIF/WebP 480/960/1440 + `photos.json` + `CREDITS.md`;
  `tools/photos/audit.py` compares fingerprints (also against the film photos and posters); `check.py` fails if a slot
  is used on two pages or if general-insurance wording appears. Missing photos (the five city headers, a closer
  personal-accident photo) are downloaded on GitHub by the workflow «Site photos» (`.github/workflows/photos.yml`,
  runs on pushes to `preview` that touch the manifest; optional secret `PIXABAY_API_KEY`, otherwise Openverse CC0/PD);
  review `tools/photos/fetched/sheet.jpg`.
- Social-preview cards: one per page and language, typography only (`tools/make_og.py` → `assets/img/og/`).
- Russian text uses Cyrillic-only subsets of Inter and Lora (renamed FG Display Cyr), OFL, `assets/fonts/OFL-*.txt`.
- 14 Oct 2026 features: needs check in the booking form (answers go with the request note), Questions and answers page
  (schema.org FAQPage), Changes in your life page (per-event checklists, each printable), print views on every page,
  breadcrumbs (BreadcrumbList).
- Premium print (15 Oct 2026, owner: everything printed or downloaded must look made with absolute care): every page
  prints as an A4 document with the GF lockup, the date and the page address on top, his details (life-insurance
  capacity and ICCS reg. no., mobile, office line, office address, website; no insurer, no e-mail) and the page's own
  QR code at the end, and name + page numbers in the margins (`print_head`/`print_foot` in build.py, site.css print
  block). The checklist PDFs (`tools/make_pdfs.py`, 4 × el/en/ru) use the same design, with a notes area and the QR
  code of the Guides page; regenerate with `python3 tools/make_pdfs.py` (CHROMIUM=… names the browser if needed).
- Christmas 2026 and the shorter home page (25 Nov 2026, owner: «κάνε τα μοναδικά και χριστουγεννιάτικα», the home page
  was too long). Home page: the solutions and the guides are rows that scroll sideways (`rail()`, `assets/js/home.js`),
  «why / how / about me» is one tabbed section, the silent film band is gone; on a phone the page is about 30% shorter
  even with the doors. Season: `XMAS = True` in build.py adds `assets/css/xmas.css` and the class `xmas` on every page
  (lights under the header, night sky, village skyline, a wish in the footer); set it to False after 6 Jan.
  «24 πόρτες ως τα Χριστούγεννα» (Greek home page only): `tools/xmas/doors.json` holds the 24 phrases and thoughts; a
  door has a film once `assets/xmas/porta-NN.mp4` + `porta-NN.jpg` + `tile-NN.jpg` exist (720×1280 from the countdown
  videos), and only those days are written into the page. Doors open by the visitor's clock at 18:00 Cyprus time of
  their day (fixed UTC times in home.js); the newest open door is the hero's film of the day. The Christmas film
  itself: `assets/xmas/liga-vimata-piso.mp4` + `.jpg`, opens 25 Dec 09:00. In the owner's preview only, `?day=7` shows
  the page as on the evening of 7 Dec.
- The 2026 refresh (25 Nov 2026, owner: more individual, more professional, more of what sites can do today):
  `assets/css/next.css` and `assets/js/fx.js` on every page, and they stay after Christmas. Headings in Literata 72pt
  SemiBold (the films' caption face; GFS Didot stays for the name, the motto, quotes and the doors' numbers), teal
  (`--teal`) for links, focus and other things you press, lit-gold primary buttons on dark, a glass header once the
  page has scrolled, hairline cards lit under the pointer. Seasonal interactions (xmas.css, home.js, fx.js): the Santa
  hat on the monogram, bulbs that can be tapped, lamp light under the pointer, doors that lean, closed doors that
  answer a knock with their date, a clock to the next door, the door's picture growing into its film.
