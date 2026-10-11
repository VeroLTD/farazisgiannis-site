# Video sources

The short videos in this folder were made on 11 October 2026 by `tools/make_videos.py` from the photographs below: slow
camera moves and dissolves, no text and no sound. Every photograph is CC0 1.0 (public domain dedication) — free to use,
also commercially, without attribution; listed here anyway so each one can be traced. They are the full-size files of
photos already in the AVRASTRO photo library (vero-os `apps/website/content/photos/credits.json`), downloaded by
Openverse id with vero-os `tools/website/fetch_originals.py`, which accepts CC0 / public domain only.

| Photo | Title | Photographer | Source page | Licence | Openverse id | Used in |
|---|---|---|---|---|---|---|
| a-trial | Work Business | Kristin Hardwick | [stocksnap](https://stocksnap.io/photo/work-business-J5LXKNDREC) | CC0 1.0 | `258657f8-c9f4-4ea8-947b-fa9dad20ad52` | film-how |
| art-education | Child Home | Direct Media | [stocksnap](https://stocksnap.io/photo/child-home-NIUIDH2GSG) | CC0 1.0 | `af66520a-6bcb-4eba-acea-6b1b8ca4d747` | film-guides |
| art-whole-life | Family Breakfast | Direct Media | [stocksnap](https://stocksnap.io/photo/family-breakfast-SHZ91GEEC2) | CC0 1.0 | `43c2602e-3efe-4217-a064-90e1b3ca487f` | film-solutions |
| c-guides | Woman Reading | Burst | [stocksnap](https://stocksnap.io/photo/woman-reading-VJM1ZWXLPY) | CC0 1.0 | `ba7f0e82-efc6-4fe8-a12b-804c45c1c361` | film-guides |
| c4-family | Family Portrait | Family Moments | [stocksnap](https://stocksnap.io/photo/family-portrait-OIUD9DEKPG) | CC0 1.0 | `641c4cfb-686c-4e53-baf8-4ff66464f291` | film-home |
| c4-retirement | Senior Couple | Senior Living | [stocksnap](https://stocksnap.io/photo/senior-couple-SZAKISHIN7) | CC0 1.0 | `44b0e8ae-1e9f-4a5f-b428-16af5e77f014` | film-home |
| contact-hero | Business Meeting | Christina Morillo | [stocksnap](https://stocksnap.io/photo/business-meeting-SKBXLJOILI) | CC0 1.0 | `cdab127b-2f35-4ecf-a0ee-243caeedb51d` | film-how |
| q-health | Doctor Patient | Direct Media | [stocksnap](https://stocksnap.io/photo/doctor-patient-7NQJS4WWQW) | CC0 1.0 | `b25a51ed-15ae-408d-ba2f-304dafe0803e` | film-solutions |
| q-priorities | Couple Food | Living Together | [stocksnap](https://stocksnap.io/photo/couple-food-H8DMCLKYO8) | CC0 1.0 | `9d98808c-9885-49cc-ab92-bd91e5cccf6b` | film-how |
| r-education | People Girl | Eric Ward | [stocksnap](https://stocksnap.io/photo/people-girl-LFOKYK5LRE) | CC0 1.0 | `0b0fba7a-a0d8-442b-8fa3-fc11e268a5b8` | film-home |
| r-family | Baby Girl | Direct Media | [stocksnap](https://stocksnap.io/photo/baby-girl-O64RHHGCIS) | CC0 1.0 | `d5222690-0da6-438b-bba4-7cadb53703dc` | film-home |
| r-health | Caregiver Nurse | Direct Media | [stocksnap](https://stocksnap.io/photo/caregiver-nurse-QQEQNVMB0I) | CC0 1.0 | `d1d52d6c-ac3c-42dc-a53e-e30403be3caa` | film-home |
| t-checkup | Paperwork Desk | Matt Moloney | [stocksnap](https://stocksnap.io/photo/paperwork-desk-A5DG6YREVH) | CC0 1.0 | `9346c59b-6d67-42ec-90ca-3a12788250bc` | film-guides |
| t-mortgage | House Keys | — | [rawpixel](https://www.rawpixel.com/image/5969541/house-keys) | CC0 1.0 | `d02070cd-81a9-4afb-9197-7ec5b68866f5` | film-solutions |
| t-retirement | Couple Park | Senior Living | [stocksnap](https://stocksnap.io/photo/couple-park-GL9XJQTLJK) | CC0 1.0 | `f25a67e0-e2c3-4918-a19b-fe9e1a65bd8f` | film-solutions |
| t-score | Business Working | Marc Chouinard | [stocksnap](https://stocksnap.io/photo/business-working-PHE63L27S6) | CC0 1.0 | `edbc60b2-a14c-463b-9c20-3126e200e1ee` | film-how |

Films: `film-home` (home page, beside the motto), `film-solutions`, `film-how`, `film-guides` (headers of those pages).
Each comes as `.webm` (VP9) and `.mp4` (H.264) plus `.jpg` (first frame). The site plays them only while on screen, never
for visitors who ask for less motion or to save data, and each has a pause button (`assets/js/site.js`).

## Narrated explainer films (11 Oct 2026) — assets/video/explainers/

Made in the AVRASTRO repository (VeroLTD/vero-os, `tools/video`) and copied here by `tools/add_explainers.py`:
"Giannis Farazis" (home page and About) and six subject films (Solutions: life, health, accident → income protection,
retirement, savings, education), in Greek and English, with captions (WebVTT). They play only when the visitor presses
play. Sources: AVRASTRO's own graphics, screens with demo data and music; narration by an ElevenLabs voice (the owner's
account; third person, never speaking as Giannis); moving footage from Pixabay under the Pixabay Content License — the
full list with creators is in vero-os `docs/website/VIDEO_CREDITS.md`.
