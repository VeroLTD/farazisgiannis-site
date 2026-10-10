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
