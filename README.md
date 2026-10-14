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
