#!/usr/bin/env python3
"""farazisgiannis.com — builds the static site (Greek at /, English at /en/) into ./site.

Content follows the owner's brief of 10 Oct 2026 (FARAZIS_GIANNIS_CLAUDE_WEBSITE_BRIEF_UPDATED_2026-10-10.md):
insurance work only; career since 2024; Nicosia, all of Cyprus; Greek and English; only the professional mobile
+357 97 840941 (office +357 22 124867 approved); Eurolife ONLY in the contact section; no e-mail published; the
contact form is e-mailed by the owner's own server (app.avrastro.com/v1/enquiry) and not stored; no analytics, no
cookies. Design v2 (owner feedback 10 Oct 22:25): full logo in the header (no name text beside it), a photo for every
topic (CC0 photos from the AVRASTRO library, assets/img/photos/CREDITS.md), richer layout in AVRASTRO's quality.
Ideas track (14 Oct 2026, preview branch): «Πάρτε με τηλέφωνο» call-back form (8; assets/js/callback.js → avrastro.com
contact endpoint), first meeting page (10), city pages (4), staff talks for employers (12), digital card /card/ with vCard
and QR code (42; tools/qr.py), free checklist PDFs (7; tools/checklists.py + tools/make_pdfs.py), client stories frame
(5; STORIES, empty: the page is built only with stories whose written consent is on file).
Run: python3 build.py  (no dependencies; the PDFs are pre-built, fontTools/Playwright only for tools/make_pdfs.py)
"""
import html, json, os, shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'site')
BASE = 'https://farazisgiannis.com'
UPDATED = '2026-10-14'   # privacy page "last updated" (call-back requests added 14 Oct 2026)
ASSET_V = '2026-10-15'   # cache key of site.css / site.js, and the sitemap date (ideas track pages added 14 Oct 2026)
PHONE = '+357 97 840941'; TEL = '+35797840941'
OFFICE = '+357 22 124867'; OFFICE_TEL = '+35722124867'
WHATSAPP = 'https://wa.me/35797840941'
LINKEDIN = 'https://www.linkedin.com/in/giannis-farazis-209221350/'
AVRASTRO = 'https://avrastro.com'
ENQUIRY = 'https://app.avrastro.com/v1/enquiry'
# online booking (ideas track 2, 14 Oct 2026): avrastro.com's own booking system, same free times and bookings
BOOKING_API = os.environ.get('BOOKING_API', AVRASTRO + '/wp-json/vero/v1')
# the owner's preview (/preview/, branch preview): a visible banner, pages waiting for approval, placeholders shown
PREVIEW = os.environ.get('PREVIEW') == '1'
OWN_REG = '7854'   # owner 14 Oct 2026
# Russian edition (owner 14 Oct 2026: a Russian-speaking colleague in the office). Pages are rendered from the English
# ones and every text segment is mapped through i18n/ru.json (python3 tools/ru_segments.py --missing lists what is
# left). Built in the preview; on the real site only once the colleague has checked the texts (RU_LIVE = True).
RU_LIVE = True   # 15 Oct 2026: the Russian-speaking colleague checked the texts; owner approved
_ru_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'i18n', 'ru.json')
RU = json.load(open(_ru_file, encoding='utf-8')) if os.path.exists(_ru_file) else {}
RU_ON = bool(RU) and (PREVIEW or RU_LIVE)
LANGS = ['el', 'en'] + (['ru'] if RU_ON else [])
RENDER = {'ru': False}   # True while an English page is being rendered for the Russian edition   # Giannis's own ICCS registration number (law 38(I)/2016 art. 359(6)); shown in the footer once filled

SLUGS = {
    'home': {'el': '', 'en': ''},
    'about': {'el': 'sxetika', 'en': 'about'},
    'solutions': {'el': 'lyseis', 'en': 'solutions'},
    'how': {'el': 'pos-douleuo', 'en': 'how-i-work'},
    'guides': {'el': 'odigoi', 'en': 'guides'},
    'contact': {'el': 'epikoinonia', 'en': 'contact'},
    'booking': {'el': 'rantevou', 'en': 'book'},
    'first': {'el': 'proti-synantisi', 'en': 'first-meeting'},
    'employers': {'el': 'enimerosi-prosopikou', 'en': 'staff-talks'},
    'card': {'el': 'card', 'en': 'card'},
    'stories': {'el': 'istories', 'en': 'stories'},
    'faq': {'el': 'syxnes-erotiseis', 'en': 'faq'},
    'events': {'el': 'allages-zois', 'en': 'life-events'},
    'privacy': {'el': 'aporrito', 'en': 'privacy'},
}
NAV = ['about', 'solutions', 'how', 'guides', 'contact']
T = {
    'name': {'el': 'Γιάννης Φαραζής', 'en': 'Giannis Farazis'},
    'role': {'el': 'Ασφαλιστικός Σύμβουλος', 'en': 'Insurance Advisor'},
    'nav': {
        'about': {'el': 'Σχετικά', 'en': 'About'}, 'solutions': {'el': 'Λύσεις', 'en': 'Solutions'},
        'how': {'el': 'Πώς δουλεύω', 'en': 'How I work'}, 'guides': {'el': 'Οδηγοί', 'en': 'Guides'},
        'contact': {'el': 'Επικοινωνία', 'en': 'Contact'}, 'privacy': {'el': 'Απόρρητο', 'en': 'Privacy'},
        'booking': {'el': 'Κλείστε ραντεβού', 'en': 'Book an appointment'},
        'first': {'el': 'Πρώτη συνάντηση: τι να φέρω', 'en': 'Your first meeting: what to bring'},
        'employers': {'el': 'Ενημέρωση για το προσωπικό σας', 'en': 'A talk for your staff'},
        'card': {'el': 'Ψηφιακή κάρτα', 'en': 'Digital business card'},
        'stories': {'el': 'Ιστορίες πελατών', 'en': 'Client stories'},
        'faq': {'el': 'Συχνές ερωτήσεις', 'en': 'Questions and answers'},
        'events': {'el': 'Αλλαγές στη ζωή σας', 'en': 'Changes in your life'},
        'home': {'el': 'Αρχική', 'en': 'Home'},
        'cities': {'el': 'Πόλεις', 'en': 'Cities'},
    },
    'call': {'el': 'Καλέστε', 'en': 'Call'},
    'menu': {'el': 'Μενού', 'en': 'Menu'},
    'skip': {'el': 'Μετάβαση στο περιεχόμενο', 'en': 'Skip to content'},
    'other': {'el': 'English', 'en': 'Ελληνικά'},
    'where': {'el': 'Λευκωσία · εξυπηρέτηση σε όλη την Κύπρο · Ελληνικά και Αγγλικά', 'en': 'Nicosia · serving clients across Cyprus · Greek and English'},
    'motto': {'el': 'Μαζί σου, κάθε στιγμή.', 'en': 'With you, every moment.'},
    'triad': {'el': 'Προστασία | Αποταμίευση | Ηρεμία', 'en': 'Protection | Savings | Peace of mind'},
    'more': {'el': 'Περισσότερα', 'en': 'Read more'},
    'foot': {'el': 'Ασφαλιστικός Σύμβουλος στην Κύπρο. Οι πληροφορίες του ιστότοπου είναι γενικές και δεν αποτελούν εξατομικευμένη συμβουλή.',
             'en': 'Insurance Advisor in Cyprus. The information on this website is general and is not personal advice.'},
}

def L(v, lang): return v[lang] if isinstance(v, dict) else v
def esc(s): return html.escape(s, quote=True)
def url(page, lang, anchor=''):
    slug = SLUGS[page]['en' if lang == 'ru' else lang]
    return {'en': '/en/', 'ru': '/ru/'}.get(lang, '/') + (slug + '/' if slug else '') + (('#' + anchor) if anchor else '')

ICON = {
    'cal': '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    'phone': '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 3h3l2 5-2.5 1.5a11 11 0 0 0 7 7L16 14l5 2v3a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    'wa': '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20l1.3-3.8A8 8 0 1 1 8 19z"/><path d="M9 9.5c.3 2 2.2 4.2 4.5 4.8l1.2-1.1 1.8.8c-.2 1-1 1.8-2 1.8A6 6 0 0 1 8 9.8c0-1 .8-1.8 1.8-2l.8 1.8z"/></svg>',
    'clear': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M10 8h20l8 8v24H10z"/><path d="M30 8v8h8"/><path d="M16 24h16M16 30h16M16 36h10"/></svg>',
    'calm': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="24" cy="24" r="16"/><path d="M17 27c2 3 4.5 4.5 7 4.5s5-1.5 7-4.5"/><path d="M18 19h.01M30 19h.01" stroke-width="3" stroke-linecap="round"/></svg>',
    'with': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M24 40s-14-8.5-14-19a8 8 0 0 1 14-5.3A8 8 0 0 1 38 21c0 10.5-14 19-14 19z"/></svg>',
    'cy': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M24 42s13-12 13-23a13 13 0 0 0-26 0c0 11 13 23 13 23z"/><circle cx="24" cy="19" r="4.5"/></svg>',
    'check': '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 10.5l4 4 8-9"/></svg>',
    'arrow': '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 10h11M11 5l5 5-5 5"/></svg>',
}
def _i(paths):   # a 24px line icon in the site's style (1.6 stroke, round joins); decorative, so hidden from screen readers
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
# topic and page icons (14 Oct 2026 design pass): icon cards where a photo would repeat one used elsewhere
ICON.update({
    't-life': _i('<path d="M12 21s-7-4.4-7-10V5.5L12 3l7 2.5V11c0 5.6-7 10-7 10z"/><path d="M12 15.5s-3.2-2-3.2-4.3a1.8 1.8 0 0 1 3.2-1.2 1.8 1.8 0 0 1 3.2 1.2c0 2.3-3.2 4.3-3.2 4.3z"/>'),
    't-health': _i('<rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M12 8v8M8 12h8"/>'),
    't-accident': _i('<rect x="2.6" y="8.2" width="18.8" height="7.6" rx="3.8" transform="rotate(-45 12 12)"/><path d="M10.6 10.6h.01M13.4 13.4h.01M10.6 13.4h.01M13.4 10.6h.01"/>'),
    't-retirement': _i('<path d="M3 18h18M5.5 18a6.5 6.5 0 0 1 13 0"/><path d="M12 5.5V7.5M5.4 8.4l1.4 1.4M18.6 8.4l-1.4 1.4M3 21h18"/>'),
    't-savings': _i('<ellipse cx="12" cy="6.5" rx="7" ry="2.8"/><path d="M5 6.5v5c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-5M5 11.5v5c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-5"/>'),
    't-education': _i('<path d="M2.5 9.5 12 5l9.5 4.5L12 14z"/><path d="M6.5 11.5v4.2c0 1.3 2.5 2.8 5.5 2.8s5.5-1.5 5.5-2.8v-4.2M21.5 9.5v5"/>'),
    't-loan': _i('<path d="M3.5 11 12 4l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><circle cx="12" cy="13.5" r="1.8"/><path d="M12 15.3V18"/>'),
    't-business': _i('<rect x="3" y="7.5" width="18" height="12.5" rx="2"/><path d="M8.5 7.5V5.5a1.5 1.5 0 0 1 1.5-1.5h4a1.5 1.5 0 0 1 1.5 1.5v2M3 13h18"/>'),
    't-review': _i('<path d="M6 3h8.5L19 7.5V21H6z"/><path d="M14 3v5h5"/><path d="m9 14.5 2 2 4-4.5"/>'),
    't-group': _i('<circle cx="9" cy="8" r="3"/><path d="M3.5 19.5a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 14.3a4.5 4.5 0 0 1 5.5 4.4"/>'),
    't-expats': _i('<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.3 2.4 3.4 5.2 3.4 8.5s-1.1 6.1-3.4 8.5c-2.3-2.4-3.4-5.2-3.4-8.5s1.1-6.1 3.4-8.5z"/>'),
    'office': _i('<path d="M4 20.5V5.5L13 3v17.5M13 9h7v11.5M2.5 20.5h19"/><path d="M7.5 8h2M7.5 11.5h2M7.5 15h2M16 12.5h1.5M16 16h1.5"/>'),
    'video': _i('<rect x="2.5" y="6" width="13" height="12" rx="2.5"/><path d="m15.5 10.5 6-3.5v10l-6-3.5"/>'),
    'pin': _i('<path d="M12 21s-6.5-6-6.5-11.5a6.5 6.5 0 0 1 13 0C18.5 15 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.3"/>'),
    'clock': _i('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
    'nosign': _i('<path d="M4 20h7M14.5 4.5l5 5L10 19l-5.5.5L5 14z"/><path d="M3 3l18 18"/>'),
    'ways': _i('<path d="M4 5h11a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H9l-4 3.5V15H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><path d="M17 9h3a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-1v2.5L16 19h-3"/>'),
    'print': _i('<path d="M6.5 9V3.5h11V9"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M6.5 14h11v6.5h-11z"/>'),
    'question': _i('<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.4a2.5 2.5 0 0 1 4.8.9c0 1.7-2.4 2.1-2.4 3.7M12 16.8h.01"/>'),
    'list': _i('<path d="M9 6.5h11M9 12h11M9 17.5h11"/><path d="m3.5 6.5 1.2 1.2L6.8 5.5M3.5 12l1.2 1.2 2.1-2.2M3.5 17.5l1.2 1.2 2.1-2.2"/>'),
    'ring': _i('<circle cx="9" cy="14" r="5.5"/><circle cx="15" cy="14" r="5.5"/><path d="m10.5 4.5 1.5 2 1.5-2"/>'),
    'baby': _i('<circle cx="12" cy="8" r="4"/><path d="M10.6 7.6h.01M13.4 7.6h.01M10.8 9.6c.7.5 1.7.5 2.4 0"/><path d="M5.5 21a6.5 6.5 0 0 1 13 0"/>'),
    'work': _i('<rect x="3" y="7.5" width="18" height="12.5" rx="2"/><path d="M8.5 7.5V5.5a1.5 1.5 0 0 1 1.5-1.5h4a1.5 1.5 0 0 1 1.5 1.5v2"/><path d="m9 13.5 2 2 4-4"/>'),
    'move': _i('<path d="M3 19h18"/><path d="M5 19V8.5l5-3.5 5 3.5V19"/><path d="M15 12h4l2 3v4"/><circle cx="8" cy="19" r=".01"/>'),
    'loss': _i('<path d="M12 20.5s-7.5-4.6-7.5-10.3A4.2 4.2 0 0 1 12 7.6a4.2 4.2 0 0 1 7.5 2.6c0 5.7-7.5 10.3-7.5 10.3z"/><path d="M12 7.6v12.9"/>'),
    'cap': _i('<path d="M2.5 9.5 12 5l9.5 4.5L12 14z"/><path d="M6.5 11.5v4.2c0 1.3 2.5 2.8 5.5 2.8s5.5-1.5 5.5-2.8v-4.2"/>'),
    'sun': _i('<path d="M3 18h18M5.5 18a6.5 6.5 0 0 1 13 0M12 5.5V7.5M5.4 8.4l1.4 1.4M18.6 8.4l-1.4 1.4"/>'),
})
TOPIC_ICON = {'life': 't-life', 'health': 't-health', 'accident': 't-accident', 'retirement': 't-retirement', 'savings': 't-savings', 'education': 't-education',
              'loan': 't-loan', 'business': 't-business', 'group': 't-group', 'expats': 't-expats', 'review': 't-review'}

LINES = ('<svg class="lines" viewBox="0 0 400 400" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2">'
         '<path d="M330 40H190A150 150 0 0 0 60 255"/><path d="M330 92H150"/><path d="M215 92 55 252"/>'
         '<path d="M330 190H180L40 330"/><path d="M220 190 80 330"/><path d="M262 214 168 308"/>'
         '<path d="M330 190A150 150 0 0 1 120 330"/></svg>')

# Photos (14 Oct 2026 audit): one photograph per place on one page, never repeated (tools/photos/manifest.json, checked by
# tools/photos/audit.py and check.py). AVIF and WebP in 480/960/1440 px, alt text in Greek, English and Russian.
_PJ = os.path.join(ROOT, 'assets', 'img', 'photos', 'photos.json')
PHOTOS = json.load(open(_PJ, encoding='utf-8')) if os.path.exists(_PJ) else {}
for _p in PHOTOS.values():   # the Russian page is rendered from the English one: its alt texts come from the manifest
    if _p['alt'].get('ru'): RU.setdefault(_p['alt']['en'], _p['alt']['ru'])

def photo(key, lang='el', cls='', eager=False, sizes='(max-width: 600px) 100vw, (max-width: 960px) 50vw, 380px'):
    """<picture> with AVIF and WebP sources; '' when the slot has no photo yet (e.g. waiting for the photo workflow)."""
    p = PHOTOS.get(key)
    if not p: return ''
    ws = p['widths']; base = f'/assets/img/photos/{key}'
    srcset = lambda ext: ', '.join(f'{base}-{w}.{ext} {w}w' for w in ws)
    fallback = max([w for w in ws if w <= 960] or ws)
    alt = p['alt']['en' if lang == 'ru' else lang]
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}"><source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img class="{cls}" src="{base}-{fallback}.webp" width="{fallback}" height="{round(fallback / 1.5)}" alt="{esc(alt)}" data-photo="{key}"'
            + (' fetchpriority="high"' if eager else ' loading="lazy"') + ' decoding="async"></picture>')

def print_button(lang):
    """«Print» (site.js); the print view (site.css @media print) leaves out menus, forms, films and the closing band"""
    return f'<p class="page-head__tools no-print"><button class="btn btn-ghost btn-sm" type="button" data-print>{ICON["print"]}{"Εκτύπωση" if lang == "el" else "Print"}</button></p>'

def icon_panel(name, cls=''):
    """the place of a photo, filled with a large line icon on the site's colours (no photo repeated)"""
    return f'<div class="icon-panel {cls}" aria-hidden="true">{ICON[name]}</div>'

def film(name, lang, cls=''):
    """A short silent loop made from CC0 photos (tools/make_videos.py, assets/video/SOURCES.md). The first frame shows
    until site.js starts it: only while it is on screen, never for visitors who ask for less motion or to save data.
    Decorative, so hidden from screen readers; a small button pauses and resumes it."""
    v = f'/assets/video/{name}'
    pause, play = ('Παύση βίντεο', 'Αναπαραγωγή βίντεο') if lang == 'el' else ('Pause video', 'Play video')
    return (f'<div class="film {cls}"><video class="film__video" muted loop playsinline preload="none" poster="{v}.jpg" aria-hidden="true" tabindex="-1" disablepictureinpicture>'
            f'<source src="{v}.webm" type="video/webm"><source src="{v}.mp4" type="video/mp4"></video>'
            f'<button class="film__toggle" type="button" hidden data-pause="{pause}" data-play="{play}" aria-label="{pause}">'
            '<svg class="i-pause" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/></svg>'
            '<svg class="i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg></button></div>')

# Narrated explainer films (11 Oct 2026; farazisgiannis.com films and Russian versions 15 Oct 2026), made in the AVRASTRO
# repository (tools/video) and copied here by tools/add_explainers.py: assets/video/explainers/explainers.json →
# {key: {lang: {video, poster, vtt, title, description, duration, posters?}}}, lang el / en / ru. A film that is not in the
# folder yet shows nothing (the page keeps its icon or simply has no film). EXPLAINERS_JSON=<path> reads another index
# (used to test the wiring with a fixture).
_EXP = os.environ.get('EXPLAINERS_JSON') or os.path.join(ROOT, 'assets/video/explainers/explainers.json')
EXPLAINERS = json.load(open(_EXP, encoding='utf8')) if os.path.exists(_EXP) else {}
# Solutions page: the subject's film, the first of the list that exists. Loan protection is fg-loan (life only); the
# AVRASTRO film topic-loan is never shown here (it also covers the home against fire, earthquake and flood).
FILM_OF = {'life': ['topic-life'], 'health': ['topic-health'], 'accident': ['topic-income'], 'retirement': ['topic-retirement'],
           'savings': ['fg-savings', 'topic-savings'], 'education': ['topic-education'], 'business': ['topic-business'],
           'group': ['topic-group'], 'expats': ['topic-expats'], 'loan': ['fg-loan'], 'review': ['topic-review']}
NEVER_HERE = {'topic-loan'}
# the checklist films beside their PDFs on the Guides page (tools/checklists.py stems)
FILM_OF_CHECKLIST = {'eggrafa-apozimiosis': 'fg-checklist-claims', 'prin-ypograpso': 'fg-checklist-signing', 'etisios-elegxos': 'fg-yearly-check'}
# the About film opens on the portrait, which is already the page's header photo: its poster is a later frame of the
# film (add_explainers.py → posters.alt; the 14 Oct 2026 frames *-motto.jpg until the next export)
for _l in ('el', 'en', 'ru'):
    _e = EXPLAINERS.get('meet-giannis', {}).get(_l)
    _f = f'avrastro-film-meet-giannis-{_l}-motto.jpg'
    if _e and not (_e.get('posters') or {}).get('alt') and os.path.exists(os.path.join(ROOT, 'assets/video/explainers', _f)):
        _e.setdefault('posters', {})['alt'] = _f

EXP_TXT = {
    'el': {'play': 'Αναπαραγωγή βίντεο: ', 'watch': 'Δείτε το βίντεο', 'cc': 'Με υπότιτλους', 'track': 'Ελληνικά'},
    'en': {'play': 'Play the video: ', 'watch': 'Watch', 'cc': 'Captions available', 'track': 'English'},
    'ru': {'play': 'Смотреть видео: ', 'watch': 'Смотреть', 'cc': 'С субтитрами', 'track': 'Русский'},
}

def film_of(keys):
    """the first of these films that is in the site"""
    for k in ([keys] if isinstance(keys, str) else keys or []):
        if k not in NEVER_HERE and EXPLAINERS.get(k): return k
    return ''

def explainer(key, lang, cls='', poster=None):
    """A narrated film with its poster, captions (off until the visitor turns them on) and a large play button; it
    plays only when the visitor presses play. The Russian page shows the Russian film (the English one while there is
    none). poster: the name of one of the film's extra posters (add_explainers.py), so that a film shown on several
    pages does not show the same picture twice. Empty when the film is not in the site yet."""
    if key in NEVER_HERE: return ''
    fl = 'ru' if RENDER['ru'] else lang
    films = EXPLAINERS.get(key, {})
    e = films.get(fl) or (films.get('en') if fl == 'ru' else None)
    if not e:
        return ''
    el = fl if e is films.get(fl) else 'en'   # the language of the film actually shown
    tx = EXP_TXT[el]
    v = '/assets/video/explainers/'
    secs = int(round(e.get('duration', 0)))
    length = f'{secs // 60}:{secs % 60:02d}' if secs else ''
    pst = (e.get('posters') or {}).get(poster) or e['poster']
    play = tx['play'] + e['title']
    ld = {'@context': 'https://schema.org', '@type': 'VideoObject', 'name': e['title'], 'description': e.get('description') or e['title'],
          'thumbnailUrl': BASE + v + pst, 'contentUrl': BASE + v + e['video'], 'uploadDate': e.get('date', ASSET_V[:10]),
          'duration': f'PT{secs // 60}M{secs % 60}S', 'inLanguage': el}
    cc = f'<track kind="captions" src="{v}{e["vtt"]}" srclang="{el}" label="{tx["track"]}">' if e.get('vtt') else ''
    cap = f'<span class="explainer__title">{esc(e["title"])}</span>' + (f'<span>{length}</span>' if length else '') + (f'<span>{tx["cc"]}</span>' if cc else '')
    return (f'<figure class="explainer {cls}" data-film="{key}" lang="{el}"><div class="explainer__frame">'
            f'<video class="explainer__video" controls preload="none" playsinline width="1920" height="1080" poster="{v}{pst}" aria-label="{esc(e["title"])}">'
            f'<source src="{v}{e["video"]}" type="video/mp4">{cc}</video>'
            f'<button class="explainer__play" type="button" hidden aria-label="{esc(play)}"><span class="explainer__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg></span>'
            f'<span aria-hidden="true">{tx["watch"]}' + (f' <b>{length}</b>' if length else '') + '</span></button></div>'
            f'<figcaption>{cap}</figcaption>'
            '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script></figure>')

def film_band(lang, key, title, tint=False, poster=None):
    """a section with one film; nothing at all while the film is not in the site"""
    f = explainer(key, lang, 'explainer--wide', poster)
    if not f: return ''
    return (f'<section class="section section--film{" tint" if tint else ""}"><div class="wrap"><div class="section-head"><hr class="rule"><h2>{title}</h2></div>{f}</div></section>')

def portrait(alt='', cls='', eager=False, n=''):
    # 15 Oct 2026: three portraits from the owner's shoot, one per page (home, About -2, digital card -3), so none repeats
    f = 'giannis-farazis-portrait' + (f'-{n}' if n else '')
    return (f'<picture><source srcset="/assets/img/{f}.webp" type="image/webp"><img class="{cls}" src="/assets/img/{f}.jpg" '
            f'width="480" height="600" alt="{esc(alt)}"' + (' fetchpriority="high"' if eager else ' loading="lazy"') + '></picture>')

LANG_NAME = {'el': 'Ελληνικά', 'en': 'English', 'ru': 'Русский'}

def og_image(page, lang):
    """each page has its own social-preview card (tools/make_og.py: typography only, no photo, so no photo repeats)"""
    f = f'/assets/img/og/{page}-{lang}.jpg'
    return f if os.path.exists(os.path.join(ROOT, f.lstrip('/'))) else '/assets/img/og.jpg'

def head(lang, page, title, desc, extra_ld=None):
    cur = 'ru' if RENDER['ru'] else lang
    canonical = BASE + url(page, cur)
    switch = ''.join(f'<a class="lang" href="{url(page, l)}" hreflang="{l}" lang="{l}">{LANG_NAME[l]}</a>' for l in LANGS if l != cur)
    alternates = ''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE + url(page, l)}">\n' for l in LANGS)
    ld = [{
        '@context': 'https://schema.org', '@type': 'Person', '@id': BASE + '/#person',
        'name': 'Giannis Farazis', 'alternateName': ['Γιάννης Φαραζής', 'Ιωάννης Φαραζής', 'Ioannis Farazis'],
        'jobTitle': L(T['role'], lang), 'url': BASE + '/', 'image': BASE + '/assets/img/giannis-farazis-portrait.jpg',
        'telephone': TEL, 'address': {'@type': 'PostalAddress', 'addressLocality': 'Λευκωσία' if lang == 'el' else 'Nicosia', 'addressCountry': 'CY'},
        'areaServed': {'@type': 'Country', 'name': 'Κύπρος' if lang == 'el' else 'Cyprus'}, 'knowsLanguage': ['el', 'en'],
        'knowsAbout': ['Life insurance', 'Health insurance', 'Personal accident insurance', 'Retirement planning', 'Savings plans', 'Education planning', 'Loan protection', 'Group insurance'],
        'sameAs': [LINKEDIN, AVRASTRO + ('/en' if lang == 'en' else '') + '/giannis-farazis/'],
    }]
    if extra_ld: ld += extra_ld
    navlinks = ''.join(f'<a href="{url(p, lang)}"' + (' aria-current="page"' if p == page else '') + f'>{L(T["nav"][p], lang)}</a>' for p in NAV)
    return f'''<!doctype html>
<html lang="{cur}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
{alternates}<link rel="alternate" hreflang="x-default" href="{BASE + url(page, 'el')}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Giannis Farazis">
<meta property="og:locale" content="{ {'el': 'el_GR', 'en': 'en_GB', 'ru': 'ru_RU'}[cur] }">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}{og_image(page, cur)}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#142a4c">
<link rel="icon" href="/assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/GFSDidot-Regular.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ld[0], ensure_ascii=False)}</script>
</head>
<body>
{print_head(lang, canonical)}
{('<div class="preview-banner" role="note">' + ('ΠΡΟΕΠΙΣΚΟΠΗΣΗ — αλλαγές που περιμένουν έγκριση. Δεν είναι η δημοσιευμένη σελίδα.' if lang == 'el' else 'PREVIEW — changes waiting for approval. This is not the published page.') + '</div>') if PREVIEW else ''}
<a class="skip" href="#main">{L(T['skip'], lang)}</a>
<header class="site-head"><div class="wrap">
<a class="brand" href="{url('home', lang)}" aria-label="Giannis Farazis — {'Αρχική' if lang == 'el' else 'Home'}"><img src="/assets/img/gf-lockup.png" alt="Giannis Farazis — Mazi sou, kathe stigmi" width="294" height="70"></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">{L(T['menu'], lang)}</button>
<nav class="nav" id="nav" aria-label="{'Κύριο μενού' if lang == 'el' else 'Main menu'}">
{navlinks}
{switch}
<a class="nav-call" href="tel:{TEL}">{ICON['phone']}{PHONE}</a>
</nav></div></header>
<main id="main">
''' + ('<p class="ru-strip">Встречи проходят на греческом или английском языке; в нашем офисе вам поможет сотрудник, говорящий по-русски.</p>' if cur == 'ru' else '')

def reg_line(lang):
    # law 38(I)/2016 art. 359(6): an intermediary states its capacity and registration number
    if OWN_REG:
        return ' · <span>' + (('Ασφαλιστικός Σύμβουλος κλάδου ζωής, Αρ. Μητρώου ΥΕΑΕ ' if lang == 'el' else 'Life insurance advisor, ICCS Reg. No. ') + esc(OWN_REG)) + '</span>'
    return (' · [Αρ. Μητρώου ΥΕΑΕ — συμπληρώνεται πριν από τη δημοσίευση]' if lang == 'el' else ' · [ICCS Reg. No. — filled in before publication]') if PREVIEW else ''

# Print views (15 Oct 2026, owner: everything printed must be premium, with the GF brand and his details at the bottom).
# Hidden on screen (site.css .print-only); on paper: the GF lockup, his capacity, the date and the page's address on the
# first page; at the end of the page a signature block with his details and the QR code of the page (PRINT_QR is
# replaced by the page's own code when the page is written, main()); "Giannis Farazis · farazisgiannis.com" and page
# numbers in the margins of every page (site.css @page). Life business only: no insurer, no e-mail.
PRINT_QR = '<!--print-qr-->'

def print_head(lang, canonical):
    el = lang == 'el'
    return (f'<div class="print-only print-head" aria-hidden="true"><img src="/assets/img/gf-lockup.png" alt="" width="294" height="70">'
            f'<div class="print-head__meta"><p class="print-head__kicker">{"Ασφαλιστικός Σύμβουλος κλάδου ζωής" if el else "Life insurance advisor"}</p>'
            f'<p class="print-head__date" data-print-date data-lang="{lang}"></p><p>{esc(canonical.replace("https://", ""))}</p></div></div>')

def print_foot(lang):
    el = lang == 'el'
    rows = [('Κινητό' if el else 'Mobile', PHONE), ('Γραφείο' if el else 'Office', OFFICE),
            ('Διεύθυνση' if el else 'Address', OFFICE_EL if el else OFFICE_EN), ('Ιστότοπος' if el else 'Website', 'farazisgiannis.com')]
    return (f'<div class="print-only print-foot" aria-hidden="true"><div class="print-foot__row"><div class="print-foot__sign">'
            f'<img class="print-foot__mark" src="/assets/img/gf-mark.png" alt="" width="240" height="236">'
            f'<div><p class="print-foot__name">{L(T["name"], lang)}</p>'
            f'<p class="print-foot__role">{("Ασφαλιστικός Σύμβουλος κλάδου ζωής · Αρ. Μητρώου ΥΕΑΕ " if el else "Life insurance advisor · ICCS Reg. No. ") + esc(OWN_REG)}</p>'
            '<ul class="print-foot__contact">' + ''.join(f'<li><span>{k}</span>{esc(v)}</li>' for k, v in rows) + '</ul></div></div>'
            f'<div class="print-foot__qr">{PRINT_QR}<p>{"Σαρώστε για τη σελίδα online" if el else "Scan for this page online"}</p></div></div>'
            f'<p class="print-foot__note">{"Γενική ενημέρωση, όχι εξατομικευμένη συμβουλή." if el else "General information, not personal advice."}</p></div>')

def with_print_qr(doc, path):
    """the page's own QR code in its print footer (tools/qr.py, inline SVG in the site's midnight blue)"""
    if PRINT_QR not in doc: return doc
    import qr
    s = qr.svg(qr.encode(BASE + path)).replace('<svg ', '<svg class="print-foot__qr-code" aria-hidden="true" focusable="false" ', 1).replace('fill="#000"', 'fill="#142a4c"')
    s = _re.sub(r' width="\d+" height="\d+"', '', s, count=1)
    return doc.replace(PRINT_QR, s.strip())

def foot(lang):
    el = lang == 'el'
    more = ['first', 'events', 'faq', 'employers', 'card', 'privacy']
    return f'''</main>
{print_foot(lang)}
<footer class="site-foot"><div class="wrap">
<div class="foot-brand"><img src="/assets/img/gf-logo.png" alt="Giannis Farazis — Mazi sou, kathe stigmi" width="200" height="115" loading="lazy">
<p>{L(T['foot'], lang)}</p></div>
<nav class="foot-col" aria-label="{'Σελίδες' if el else 'Pages'}"><h2>{'Σελίδες' if el else 'Pages'}</h2>{''.join(f'<a href="{url(p, lang)}">{L(T["nav"][p], lang)}</a>' for p in NAV)}</nav>
<nav class="foot-col" aria-label="{'Χρήσιμα' if el else 'Useful'}"><h2>{'Χρήσιμα' if el else 'Useful'}</h2>{''.join(f'<a href="{url(p, lang)}">{L(T["nav"][p], lang)}</a>' for p in more)}</nav>
<div class="foot-col"><h2>{'Επικοινωνία' if el else 'Contact'}</h2>
<a href="tel:{TEL}">{PHONE}</a><a href="{WHATSAPP}" rel="noopener">WhatsApp</a><a href="{LINKEDIN}" rel="noopener">LinkedIn</a><a href="{url('booking', lang)}">{L(T['nav']['booking'], lang)}</a>
<span>{'Λευκωσία · Παγκύπρια' if el else 'Nicosia · all of Cyprus'}</span>
<h2 class="foot-sub">{L(T['nav']['cities'], lang)}</h2><p class="foot-cities">{' · '.join(f'<a href="{url("city-" + c[0], lang)}">{c[3] if el else c[5]}</a>' for c in CITIES)}</p></div>
</div><div class="wrap foot-legal">© {date.today().year} {L(T['name'], lang)}{reg_line(lang)}</div></footer>
<div class="callbar"><a href="tel:{TEL}">{ICON['phone']}{L(T['call'], lang)}</a><a href="{WHATSAPP}" rel="noopener">{ICON['wa']}WhatsApp</a><a href="{url('booking', lang)}">{ICON['cal']}{'Ραντεβού' if lang == 'el' else 'Book'}</a></div>
<script src="/assets/js/site.js?v={ASSET_V}" defer></script>
</body></html>
'''

def actions(lang, extra='', book=True):
    return f'''<div class="actions">
<a class="btn btn-primary" href="tel:{TEL}">{ICON['phone']}{L(T['call'], lang)} {PHONE}</a>
<a class="btn btn-ghost" href="{WHATSAPP}" rel="noopener">{ICON['wa']}WhatsApp</a>
{f'<a class="btn btn-ghost" href="{url("booking", lang)}">{ICON["cal"]}{L(T["nav"]["booking"], lang)}</a>' if book else ''}{extra}
</div>'''

def crumbs_html(lang, trail, here):
    """breadcrumbs above a page title, with schema.org BreadcrumbList: Home › … › this page"""
    items = [(L(T['nav']['home'], lang), url('home', lang))] + list(trail)
    cur = 'ru' if RENDER['ru'] else lang
    ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE + u.replace('/en/', '/ru/', 1) if cur == 'ru' else BASE + u}
        for i, (n, u) in enumerate(items)] + [{'@type': 'ListItem', 'position': len(items) + 1, 'name': here}]}
    links = ''.join(f'<li><a href="{u}">{n}</a></li>' for n, u in items)
    return (f'<nav class="crumbs" aria-label="{"Διαδρομή" if lang == "el" else "Breadcrumb"}"><ol>{links}<li aria-current="page">{here}</li></ol></nav>'
            '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>')

def page_head(title, lead, img=None, alt='', movie=None, lang='el', trail=(), kicker='', extra='', crumb=None):
    """the header band of every inner page: breadcrumbs, an optional kicker, the title, the lead, optional buttons, and a
    film or one photo of its own (a photo slot used on this page only)"""
    pic = photo(img, lang, eager=True, sizes='(max-width: 860px) 100vw, 520px') if img else ''
    media = (f'<figure class="page-head__media">{film(movie, lang)}</figure>' if movie
             else f'<figure class="page-head__media">{pic}</figure>' if pic else '')
    k = f'<p class="page-head__kicker">{kicker}</p>' if kicker else ''
    return (f'<section class="page-head on-dark{" has-media" if media else ""}"><div class="wrap"><div class="page-head__text">{crumbs_html(lang, trail, crumb or title)}'
            f'{k}<h1>{title}</h1><p class="page-head__lead">{lead}</p>{extra}</div>{media or ("<div class=page-head__deco aria-hidden=true>" + LINES + "</div>")}</div></section>')

def cta_band(lang):
    el = lang == 'el'
    return f'''<section class="cta-band on-dark"><div class="wrap">
<div class="cta-band__mark" aria-hidden="true"><img src="/assets/img/gf-mark.png" alt="" width="240" height="236" loading="lazy"></div>
<div><h2>{'Μια πρώτη συζήτηση, χωρίς δέσμευση' if el else 'A first conversation, with no commitment'}</h2>
<p>{'Καλέστε, στείλτε μήνυμα στο WhatsApp ή αφήστε τα στοιχεία σας και θα σας καλέσω εγώ.' if el else 'Call, send a WhatsApp message, or leave your details and I will call you.'}</p>
{actions(lang, f'<a class="btn btn-link" href="{url("contact", lang)}">{"Φόρμα επικοινωνίας" if el else "Contact form"}{ICON["arrow"]}</a>')}</div>
</div></section>'''

# ------------------------------------------------------------------ content
# (id, photo, title, short, long, includes[], question)
SOLUTIONS = [
    ('life', 'sol-life',
     {'el': 'Ασφάλεια ζωής', 'en': 'Life insurance'},
     {'el': 'Ένα ποσό για τους ανθρώπους σας αν δεν είστε εκεί.', 'en': 'A sum for the people you love if you are not there.'},
     {'el': 'Η ασφάλεια ζωής πληρώνει ένα ποσό στους δικαιούχους που ορίζετε. Μπορεί να εξοφλήσει ένα δάνειο, να αντικαταστήσει για κάποια χρόνια το εισόδημα που χάνεται και να κρατήσει όρθιους τους στόχους της οικογένειας, όπως τις σπουδές των παιδιών.',
      'en': 'Life insurance pays a sum to the beneficiaries you choose. It can pay off a loan, replace lost income for a number of years and keep your family’s plans on track, such as the children’s studies.'},
     [{'el': 'Κάλυψη για συγκεκριμένα χρόνια ή για όλη τη ζωή', 'en': 'Cover for a set number of years, or for life'},
      {'el': 'Πρόσθετες καλύψεις, όπως σοβαρές ασθένειες ή ανικανότητα', 'en': 'Extra cover such as serious illness or disability'},
      {'el': 'Δικαιούχους που αλλάζετε όταν αλλάζει η ζωή σας', 'en': 'Beneficiaries you can change as your life changes'}],
     {'el': 'Πόσο κεφάλαιο και για πόσα χρόνια χρειάζεται η δική σας οικογένεια;', 'en': 'How much cover, and for how many years, does your family need?'}),
    ('health', 'sol-health',
     {'el': 'Ιατροφαρμακευτική κάλυψη', 'en': 'Health and medical cover'},
     {'el': 'Ένα ιδιωτικό σχέδιο δίπλα στο ΓεΣΥ.', 'en': 'A private plan alongside GESY.'},
     {'el': 'Το ΓεΣΥ καλύπτει πολλά, όχι όμως τα πάντα. Ένα ιδιωτικό σχέδιο υγείας το συμπληρώνει, όταν θέλετε θεραπεία εκτός ΓεΣΥ, ιδιωτικό δωμάτιο, ευελιξία στον χρόνο ή κάλυψη στο εξωτερικό.',
      'en': 'GESY covers a great deal, but not everything. A private health plan complements it when you want treatment outside GESY, a private room, flexibility over timing, or cover abroad.'},
     [{'el': 'Νοσηλεία και επεμβάσεις', 'en': 'Hospital stays and operations'},
      {'el': 'Εξωνοσοκομειακά έξοδα, ανάλογα με το σχέδιο', 'en': 'Outpatient costs, depending on the plan'},
      {'el': 'Θεραπεία στο εξωτερικό, ανάλογα με το σχέδιο', 'en': 'Treatment abroad, depending on the plan'}],
     {'el': 'Τι μένει ακάλυπτο σήμερα και πόσο κοστίζει να το καλύψετε;', 'en': 'What is left uncovered today, and what would it cost to cover it?'}),
    ('accident', 'sol-accident',
     {'el': 'Προσωπικό ατύχημα', 'en': 'Personal accident'},
     {'el': 'Προστασία για τραυματισμό και για το εισόδημα που χάνεται.', 'en': 'Protection for injury, and for the income you lose.'},
     {'el': 'Ένα ατύχημα μπορεί να σταματήσει τη δουλειά για εβδομάδες ή μήνες. Η ασφάλεια προσωπικού ατυχήματος δίνει ποσά για τραυματισμό ή αναπηρία και, ανάλογα με το σχέδιο, ένα επίδομα όσο δεν μπορείτε να εργαστείτε.',
      'en': 'An accident can stop you working for weeks or months. Personal accident cover pays sums for injury or disability and, depending on the plan, an allowance while you cannot work.'},
     [{'el': 'Ποσό για μόνιμη αναπηρία από ατύχημα', 'en': 'A sum for permanent disability from an accident'},
      {'el': 'Επίδομα όσο δεν εργάζεστε, ανάλογα με το σχέδιο', 'en': 'An allowance while you cannot work, depending on the plan'},
      {'el': 'Ιατρικά έξοδα από ατύχημα', 'en': 'Medical costs from an accident'}],
     {'el': 'Πώς θα πληρώνατε τα έξοδα αν σταματούσατε να εργάζεστε για μερικούς μήνες;', 'en': 'How would you pay your bills if you stopped working for a few months?'}),
    ('retirement', 'sol-retirement',
     {'el': 'Σύνταξη', 'en': 'Retirement and pension planning'},
     {'el': 'Τακτική αποταμίευση για τα χρόνια μετά τη δουλειά.', 'en': 'Regular saving for the years after work.'},
     {'el': 'Η σύνταξη των Κοινωνικών Ασφαλίσεων σπάνια φτάνει για τη ζωή που θέλετε. Ένα συνταξιοδοτικό πρόγραμμα χτίζει σταδιακά ένα κεφάλαιο, και όσο νωρίτερα ξεκινάτε τόσο μικρότερο είναι το ποσό που χρειάζεται κάθε μήνα.',
      'en': 'A Social Insurance pension rarely covers the life you want. A pension plan builds up capital over time, and the earlier you start, the smaller the monthly amount you need.'},
     [{'el': 'Μηνιαία ή ετήσια καταβολή', 'en': 'Monthly or yearly contributions'},
      {'el': 'Κεφάλαιο ή τακτικό εισόδημα στη σύνταξη', 'en': 'A lump sum or regular income in retirement'},
      {'el': 'Φορολογική έκπτωση, όπου ισχύει', 'en': 'Tax relief, where it applies'}],
     {'el': 'Πόσο εισόδημα θέλετε στη σύνταξη και πόσο λείπει;', 'en': 'How much income do you want in retirement, and how much is missing?'}),
    ('savings', 'sol-savings',
     {'el': 'Αποταμίευση και επενδυτικά προγράμματα', 'en': 'Savings and investment-linked plans'},
     {'el': 'Μακροπρόθεσμη αποταμίευση με στόχο.', 'en': 'Long-term saving towards a goal.'},
     {'el': 'Τακτική αποταμίευση για έναν στόχο που απέχει χρόνια: ένα κεφάλαιο, ένα σπίτι, ένα μαξιλάρι ασφαλείας. Στα επενδυτικά προγράμματα η αξία ανεβαίνει και κατεβαίνει και δεν είναι εγγυημένη· το εξηγούμε καθαρά πριν αποφασίσετε.',
      'en': 'Regular saving for a goal that is years away: capital, a home, a safety cushion. In investment-linked plans the value goes up and down and is not guaranteed; we go through this clearly before you decide.'},
     [{'el': 'Στόχος και ορίζοντας χρόνου που ορίζετε εσείς', 'en': 'A goal and time horizon you set'},
      {'el': 'Επιλογή επιπέδου κινδύνου', 'en': 'A choice of risk level'},
      {'el': 'Συχνά με κάλυψη ζωής', 'en': 'Often with life cover included'}],
     {'el': 'Για πόσα χρόνια μπορείτε να αφήσετε τα χρήματα και πόσο ρίσκο αντέχετε;', 'en': 'For how many years can you leave the money, and how much risk can you live with?'}),
    ('education', 'sol-education',
     {'el': 'Παιδί και σπουδές', 'en': 'Children and education'},
     {'el': 'Το ποσό των σπουδών, έτοιμο όταν χρειαστεί.', 'en': 'The cost of studies, ready when it is needed.'},
     {'el': 'Ένα σχέδιο που μαζεύει σταδιακά το ποσό των σπουδών μέχρι την ηλικία που θα το χρειαστεί το παιδί. Συνήθως περιλαμβάνει κάλυψη του γονιού, ώστε το πλάνο να συνεχίζεται αν συμβεί κάτι.',
      'en': 'A plan that gradually builds up the cost of studies by the age your child will need it. It usually includes cover on the parent, so the plan carries on if something happens.'},
     [{'el': 'Κεφάλαιο στην ηλικία των σπουδών', 'en': 'Capital at the age of study'},
      {'el': 'Συνέχιση του πλάνου αν συμβεί κάτι στον γονιό', 'en': 'The plan carries on if something happens to the parent'},
      {'el': 'Για γονείς, παππούδες και νονούς', 'en': 'For parents, grandparents and godparents'}],
     {'el': 'Πόσα χρόνια έχετε μέχρι το πανεπιστήμιο και τι θα κοστίσει;', 'en': 'How many years until university, and what will it cost?'}),
    ('loan', 'sol-loan',
     {'el': 'Προστασία δανείου', 'en': 'Loan protection'},
     {'el': 'Το σπίτι μένει στην οικογένεια, όχι το χρέος.', 'en': 'Your family keeps the home, not the debt.'},
     {'el': 'Για ένα στεγαστικό δάνειο η τράπεζα ζητά συνήθως ασφάλεια ζωής. Βλέπουμε μαζί αν η κάλυψη ταιριάζει με το υπόλοιπο και τη διάρκεια του δανείου, και αν χρειάζεται κάτι επιπλέον για το εισόδημα της οικογένειας. Η τράπεζα ζητά επίσης ασφάλεια του σπιτιού για πυρκαγιά και σεισμό· καλό είναι το ασφαλισμένο ποσό να ελέγχεται σε κάθε ετήσια ανανέωση και μετά από κάθε ανακαίνιση ή επέκταση, ώστε να αντιστοιχεί στο σημερινό κόστος ανοικοδόμησης για τα τετραγωνικά του σπιτιού (όχι στην εμπορική του αξία) και το σπίτι να μην είναι υπασφαλισμένο σε μια ζημιά.',
      'en': 'For a mortgage the bank usually asks for life cover. We check together whether the cover matches the balance and term of the loan, and whether your family’s income needs something more. The bank also asks for home cover against fire and earthquake; it is wise to check the sum insured at every yearly renewal and after any renovation or extension, so that it matches today’s cost of rebuilding the home for its square metres (not its market value) and the home is not under-insured if something happens.'},
     [{'el': 'Κεφάλαιο ίσο με το υπόλοιπο του δανείου', 'en': 'Cover that matches the loan balance'},
      {'el': 'Εκχώρηση στην τράπεζα', 'en': 'Assignment to the bank'},
      {'el': 'Επανεξέταση όταν αλλάζει το δάνειο', 'en': 'A review when the loan changes'},
      {'el': 'Έλεγχος κάθε χρόνο ότι το ποσό ασφάλισης του σπιτιού καλύπτει την ανοικοδόμηση', 'en': 'A yearly check that the home’s sum insured covers rebuilding'}],
     {'el': 'Καλύπτει η τωρινή σας ασφάλεια ολόκληρο το υπόλοιπο του δανείου;', 'en': 'Does your current cover match the full balance of the loan?'}),
    ('business', 'sol-business',
     {'el': 'Προστασία επιχείρησης', 'en': 'Business protection'},
     {'el': 'Για τους ανθρώπους που κρατούν την επιχείρηση όρθια.', 'en': 'For the people who keep the business going.'},
     {'el': 'Σε πολλές επιχειρήσεις ένας ή δύο άνθρωποι φέρνουν το μεγαλύτερο μέρος των εσόδων. Η ασφάλεια βασικού στελέχους βοηθά να καλυφθούν τα χαμένα έσοδα και το κόστος αντικατάστασης αν λείψει ένα πρόσωπο-κλειδί. Η προστασία συνεταίρων, μαζί με γραπτή συμφωνία, επιτρέπει σε όσους μένουν να αγοράσουν το μερίδιο χωρίς να πουληθεί η επιχείρηση.',
      'en': 'In many businesses one or two people bring in most of the revenue. Key person insurance helps cover lost revenue and the cost of replacing someone critical. Partner protection, with a written agreement, lets the remaining partners buy the share without selling the business.'},
     [{'el': 'Ασφάλεια βασικού στελέχους', 'en': 'Key person insurance'},
      {'el': 'Προστασία συνεταίρων και μετόχων', 'en': 'Partner and shareholder protection'},
      {'el': 'Λύσεις για αυτοεργοδοτούμενους', 'en': 'Options for the self-employed'}],
     {'el': 'Τι θα γινόταν στην επιχείρηση αν έλειπε ένα βασικό πρόσωπο;', 'en': 'What would happen to the business if a key person were missing?'}),
    ('group', None,
     {'el': 'Ομαδικά σχέδια για εταιρείες', 'en': 'Group plans for companies'},
     {'el': 'Παροχές που βοηθούν να κρατήσετε καλούς ανθρώπους.', 'en': 'Benefits that help you keep good people.'},
     {'el': 'Ομαδικό σχέδιο υγείας που συμπληρώνει το ΓεΣΥ, ομαδική ασφάλεια ζωής και ατυχημάτων με ενιαίους όρους για όλους, και ταμείο προνοίας με εισφορές εργοδότη και εργαζομένου. Τα σχεδιάζουμε με βάση το μέγεθος, τις ηλικίες και τον προϋπολογισμό της ομάδας σας.',
      'en': 'A group health plan that complements GESY, group life and accident cover with one set of terms for everyone, and a provident fund with employer and employee contributions. We shape them around the size, ages and budget of your team.'},
     [{'el': 'Ομαδικό ιατροφαρμακευτικό σχέδιο', 'en': 'Group health plan'},
      {'el': 'Ομαδική ασφάλεια ζωής και ατυχημάτων', 'en': 'Group life and accident cover'},
      {'el': 'Ταμείο προνοίας ή ομαδικό συνταξιοδοτικό σχέδιο', 'en': 'Provident fund or group pension'}],
     {'el': 'Πόσα άτομα θέλετε να καλύψετε, και τι μπορεί να διαθέσει η επιχείρηση ανά εργαζόμενο;', 'en': 'How many people do you want to cover, and what can the business spend per employee?'}),
    ('expats', None,
     {'el': 'Για ξένους κατοίκους', 'en': 'For expats in Cyprus'},
     {'el': 'Υγεία, άδεια διαμονής, δάνειο και σύνταξη, και στα Αγγλικά.', 'en': 'Health, residence permits, mortgages and pensions, in English.'},
     {'el': 'Αν μετακομίσατε στην Κύπρο, το σύστημα μπορεί να διαφέρει από αυτό που ξέρετε. Βλέπουμε μαζί αν δικαιούστε ΓεΣΥ, την ιδιωτική ασφάλεια υγείας που ζητά συχνά η άδεια διαμονής, την ασφάλεια ζωής για το στεγαστικό δάνειο και τη σύνταξή σας.',
      'en': 'If you have moved to Cyprus, the system may be quite different from what you know. We look together at whether you are entitled to GESY, the private health cover residence permits often ask for, life cover for your mortgage, and your pension.'},
     [{'el': 'Ιδιωτική ασφάλεια υγείας για την άδεια διαμονής', 'en': 'Private health cover for your residence permit'},
      {'el': 'Ασφάλεια ζωής για στεγαστικό δάνειο', 'en': 'Life cover for your mortgage'},
      {'el': 'Σχεδιασμός σύνταξης', 'en': 'Retirement planning'}],
     {'el': 'Ποια άδεια διαμονής έχετε ή ζητάτε, και τι ακριβώς απαιτεί;', 'en': 'Which residence permit do you hold or need, and what exactly does it require?'}),
    ('review', 'sol-review',
     {'el': 'Επανεξέταση συμβολαίων', 'en': 'Policy reviews and needs analysis'},
     {'el': 'Τι καλύπτουν πραγματικά όσα ήδη έχετε.', 'en': 'What your existing policies really cover.'},
     {'el': 'Φέρνετε τα συμβόλαια που ήδη έχετε και τα βλέπουμε μαζί, με απλά λόγια: τι καλύπτουν, πού υπάρχουν κενά ή επικαλύψεις, και αν ταιριάζουν ακόμα στη ζωή σας.',
      'en': 'Bring the policies you already have and we go through them together, in plain words: what they cover, where the gaps or overlaps are, and whether they still fit your life.'},
     [{'el': 'Εικόνα όλων των καλύψεων σε μία σελίδα', 'en': 'All your cover on one page'},
      {'el': 'Κενά και επικαλύψεις', 'en': 'Gaps and overlaps'},
      {'el': 'Έλεγχος δικαιούχων και ποσών', 'en': 'A check of beneficiaries and sums'}],
     {'el': 'Πότε ξανακοιτάξατε τελευταία φορά τις καλύψεις σας;', 'en': 'When did you last look at your cover?'}),
]
STEPS = [
    ('how-talk', {'el': 'Μια πρώτη συζήτηση', 'en': 'A first conversation'},
     {'el': 'Τηλεφωνικά, με βιντεοκλήση ή από κοντά. Ακούω τι θέλετε να προστατεύσετε και τι έχετε ήδη.', 'en': 'By phone, video call or in person. I listen to what you want to protect and what you already have.'}),
    ('how-needs', {'el': 'Ανάλυση αναγκών', 'en': 'Looking at your needs'},
     {'el': 'Βλέπουμε μαζί οικογένεια, εισόδημα, δάνεια και στόχους, και πού βρίσκονται τα κενά.', 'en': 'Together we look at family, income, loans and goals, and where the gaps are.'}),
    ('how-proposal', {'el': 'Πρόταση με απλά λόγια', 'en': 'A proposal in plain words'},
     {'el': 'Τι καλύπτει, τι δεν καλύπτει και πόσο κοστίζει. Χωρίς πίεση για απόφαση την ίδια μέρα.', 'en': 'What it covers, what it does not and what it costs. No pressure to decide on the day.'}),
    ('how-after', {'el': 'Δίπλα σας και μετά', 'en': 'With you afterwards'},
     {'el': 'Επανεξέταση όταν αλλάζει η ζωή σας, και βοήθεια όταν χρειαστεί να κάνετε απαίτηση.', 'en': 'A review as your life changes, and help when you need to make a claim.'}),
]
VALUES = [
    ('clear', {'el': 'Καθαρές εξηγήσεις', 'en': 'Clear explanations'},
     {'el': 'Τι καλύπτεται, τι όχι και τι κοστίζει, χωρίς ψιλά γράμματα και χωρίς ορολογία.', 'en': 'What is covered, what is not and what it costs, without small print or jargon.'}),
    ('calm', {'el': 'Χωρίς πίεση', 'en': 'No pressure'},
     {'el': 'Αποφασίζετε όταν είστε έτοιμοι. Η πρώτη συζήτηση δεν σας δεσμεύει σε τίποτα.', 'en': 'You decide when you are ready. The first conversation commits you to nothing.'}),
    ('with', {'el': 'Δίπλα σας και μετά', 'en': 'There afterwards'},
     {'el': 'Στις αλλαγές της ζωής σας και όταν χρειαστεί μια αποζημίωση.', 'en': 'As your life changes, and when you need to claim.'}),
    ('cy', {'el': 'Σε όλη την Κύπρο', 'en': 'Across Cyprus'},
     {'el': 'Από κοντά στη Λευκωσία ή με βιντεοκλήση, στα Ελληνικά ή στα Αγγλικά.', 'en': 'In person in Nicosia or by video call, in Greek or English.'}),
]
GUIDES = [
    ('life-cover', 'guide-life', {'el': 'Πόση ασφάλεια ζωής χρειάζεστε;', 'en': 'How much life insurance do you need?'},
     {'el': 'Ένας απλός τρόπος να υπολογίσετε το σωστό ποσό για την οικογένειά σας.', 'en': 'A simple way to work out the right amount for your family.'},
     {'el': '''<p>Ένας πρακτικός τρόπος να το υπολογίσετε: προσθέστε τα δάνεια που θα έμεναν, το εισόδημα που θα χρειαζόταν η οικογένεια για όσα χρόνια την αφορά, και μεγάλους στόχους όπως οι σπουδές των παιδιών. Από αυτό αφαιρέστε καλύψεις και αποταμιεύσεις που ήδη έχετε.</p>
<p>Η ασφάλεια που ζητά η τράπεζα για το στεγαστικό καλύπτει το δάνειο, όχι το εισόδημα της οικογένειας. Αν φορολογείστε στην Κύπρο, τα ασφάλιστρα ζωής εκπίπτουν από το φορολογητέο εισόδημα έως το 7% του κεφαλαίου ασφάλισης, μέσα στο συνολικό όριο του ενός πέμπτου του εισοδήματος για τις σχετικές εκπτώσεις.</p>''',
      'en': '''<p>A practical way to work it out: add the loans that would remain, the income your family would need for as many years as it matters, and big goals such as your children’s studies. Then subtract the cover and savings you already have.</p>
<p>The cover a bank asks for with a mortgage pays off the loan; it does not replace your family’s income. If you pay tax in Cyprus, life premiums are deductible from taxable income up to 7% of the sum insured, within the overall limit of one fifth of income for the related deductions.</p>'''}),
    ('gesy', 'guide-gesy', {'el': 'ΓεΣΥ και ιδιωτικό σχέδιο υγείας', 'en': 'GESY and a private health plan'},
     {'el': 'Τι καλύπτει το ΓεΣΥ και πότε αξίζει ένα ιδιωτικό σχέδιο.', 'en': 'What GESY covers, and when a private plan is worth it.'},
     {'el': '''<p>Το ΓεΣΥ καλύπτει προσωπικό γιατρό, ειδικούς, εξετάσεις, φάρμακα και νοσηλεία σε παρόχους που συμμετέχουν. Ένα ιδιωτικό σχέδιο δεν το αντικαθιστά· το συμπληρώνει όταν θέλετε θεραπεία εκτός ΓεΣΥ, κάλυψη στο εξωτερικό, ιδιωτικό δωμάτιο ή ευελιξία στον χρόνο της θεραπείας.</p>
<p>Πριν επιλέξετε σχέδιο, ελέγξτε το ετήσιο όριο, την απαλλαγή, τις περιόδους αναμονής, τι ισχύει για παθήσεις που έχετε ήδη και σε ποιες χώρες ισχύει η κάλυψη.</p>''',
      'en': '''<p>GESY covers a personal doctor, specialists, tests, medicines and hospital care with participating providers. A private plan does not replace it; it complements it when you want treatment outside GESY, cover abroad, a private room or flexibility over when you are treated.</p>
<p>Before you choose a plan, check the annual limit, the excess, waiting periods, what applies to conditions you already have, and which countries are covered.</p>'''}),
    ('review', 'guide-review', {'el': 'Πότε να επανεξετάσετε τα συμβόλαιά σας', 'en': 'When to review your policies'},
     {'el': 'Οι στιγμές της ζωής που αλλάζουν τις ανάγκες σας.', 'en': 'The moments in life that change what you need.'},
     {'el': '''<p>Ένα συμβόλαιο που ταίριαζε πριν από πέντε χρόνια μπορεί σήμερα να καλύπτει λίγα ή να επικαλύπτεται με άλλο. Αξίζει μια επανεξέταση όταν παντρεύεστε, αποκτάτε παιδί, παίρνετε ή εξοφλείτε δάνειο, αλλάζετε δουλειά ή εισόδημα, και τουλάχιστον μία φορά τον χρόνο.</p>
<p>Φέρτε τα συμβόλαια που έχετε και τα βλέπουμε μαζί: τι καλύπτουν, ποιοι είναι οι δικαιούχοι και τι λείπει.</p>''',
      'en': '''<p>A policy that fitted five years ago may cover too little today, or overlap with another. A review is worth it when you marry, have a child, take out or pay off a loan, change job or income, and at least once a year.</p>
<p>Bring the policies you have and we look at them together: what they cover, who the beneficiaries are and what is missing.</p>'''}),
]

def sol_cards(lang, items=SOLUTIONS, photos=True, cls=''):
    """subject cards: with the subject's own photo (home page only), or with its icon (everywhere else)"""
    def media(sid, img):
        pic = photo(img, lang) if (photos and img) else ''
        return f'<figure>{pic}</figure>' if pic else icon_panel(TOPIC_ICON.get(sid, 't-review'), 'icon-panel--card')
    return f'<ul class="cards{cls}">' + ''.join(
        f'<li class="card"><a href="{url("solutions", lang, sid)}">{media(sid, img)}'
        f'<h3>{L(t, lang)}</h3><p>{L(s, lang)}</p><span class="card__more">{L(T["more"], lang)}{ICON["arrow"]}</span></a></li>'
        for sid, img, t, s, *_ in items) + '</ul>'

def values_grid(lang):
    return '<ul class="values">' + ''.join(f'<li><span class="values__icon">{ICON[i]}</span><h3>{L(t, lang)}</h3><p>{L(d, lang)}</p></li>' for i, t, d in VALUES) + '</ul>'

def steps_grid(lang):
    """the four steps as a numbered sequence (no photos here: the How I work page has the step photos)"""
    return '<ol class="steps-line">' + ''.join(
        f'<li><span class="steps-line__n" aria-hidden="true">{i + 1}</span><h3>{L(t, lang)}</h3><p>{L(d, lang)}</p></li>' for i, (img, t, d) in enumerate(STEPS)) + '</ol>'

GUIDE_ICON = {'life-cover': 't-life', 'gesy': 't-health', 'review': 'list'}

def link_cards(lang, items):
    """text cards with an icon: (icon, title, text, href)"""
    return '<ul class="lcards">' + ''.join(
        f'<li><a href="{h}"><span class="lcards__ico">{ICON[i]}</span><span class="lcards__body"><b>{t}</b><span>{d}</span></span>{ICON["arrow"]}</a></li>'
        for i, t, d, h in items) + '</ul>'

def page_home(lang):
    el = lang == 'el'
    title = 'Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος στη Λευκωσία' if el else 'Giannis Farazis, Insurance Advisor in Nicosia, Cyprus'
    desc = ('Ασφάλεια ζωής, υγείας, σύνταξη, αποταμίευση και σπουδές παιδιών. Προσωπική καθοδήγηση σε όλη την Κύπρο, στα Ελληνικά και Αγγλικά. +357 97 840941.' if el
            else 'Life and health cover, retirement, savings and children’s education. Personal guidance across Cyprus, in Greek and English. +357 97 840941.')
    guides = link_cards(lang, [(GUIDE_ICON[gid], L(t, lang), L(st, lang), url('guides', lang, gid)) for gid, img, t, st, _ in GUIDES] + [
        ('list', L(T['nav']['events'], lang), 'Τι να ελέγξετε και ποια χαρτιά να έχετε σε κάθε μεγάλη αλλαγή.' if el else 'What to check, and which papers to have ready, at each big change.', url('events', lang)),
        ('question', L(T['nav']['faq'], lang), 'Σύντομες απαντήσεις για την πρώτη συνάντηση, το κόστος και τις αποζημιώσεις.' if el else 'Short answers about the first meeting, costs and claims.', url('faq', lang))])
    return head(lang, 'home', title, desc) + f'''
<section class="hero on-dark"><div class="wrap">
<div class="hero__text">
<p class="hero__role">{L(T['role'], lang)}</p>
<h1>{L(T['name'], lang)}</h1>
<p class="hero__lead">{'Προστασία, αποταμίευση και ηρεμία για εσάς και την οικογένειά σας, με καθαρές εξηγήσεις και χωρίς πίεση.' if el else 'Protection, savings and peace of mind for you and your family, with clear explanations and no pressure.'}</p>
<p class="hero__motto">{L(T['motto'], lang)}</p>
{actions(lang)}
<ul class="hero__facts"><li>{'Από το 2024' if el else 'Since 2024'}</li><li>{'Λευκωσία · Παγκύπρια' if el else 'Nicosia · all of Cyprus'}</li><li>{'Ελληνικά & Αγγλικά' if el else 'Greek & English'}</li></ul>
</div>
<figure class="portrait">{LINES}{portrait('Ο Γιάννης Φαραζής' if el else 'Giannis Farazis', eager=True)}</figure>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Τι μπορούμε να δούμε μαζί' if el else 'What we can look at together'}</h2>
<p class="lead">{'Ασφάλιση με βάση τις δικές σας ανάγκες: τι θέλετε να προστατεύσετε, για πόσο, και με ποιο κόστος.' if el else 'Insurance built around your own needs: what you want to protect, for how long, and at what cost.'}</p></div>
{sol_cards(lang, [x for x in SOLUTIONS if x[0] not in ('group', 'expats')])}
</div></section>

<section class="film-band on-dark"><div class="wrap">
<div class="film-band__text">
<h2 class="film-band__motto">{L(T['motto'], lang)}</h2>
<p class="film-band__triad">{L(T['triad'], lang)}</p>
<p>{'Σε κάθε στάδιο της ζωής: όταν μεγαλώνει η οικογένεια, όταν χρειάζεστε φροντίδα, όταν τα παιδιά σπουδάζουν και όταν έρθει η ώρα της σύνταξης.' if el else 'At every stage of life: as your family grows, when you need care, while your children study, and when it is time to retire.'}</p>
</div>
{film('film-home', lang, 'film--band')}
</div></section>

<section class="section tint"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Γιατί να συνεργαστούμε' if el else 'Why work with me'}</h2></div>
{values_grid(lang)}
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Πώς δουλεύω' if el else 'How I work'}</h2>
<p class="lead">{'Τέσσερα βήματα, από την πρώτη κουβέντα μέχρι τη στιγμή που θα χρειαστείτε την κάλυψη.' if el else 'Four steps, from the first conversation to the moment you need your cover.'}</p></div>
{steps_grid(lang)}
</div></section>

<section class="section tint"><div class="wrap about-teaser">
<div><hr class="rule">
<h2>{'Λίγα λόγια για μένα' if el else 'A few words about me'}</h2>
<p>{'Είμαι Ασφαλιστικός Σύμβουλος από το 2024, με βάση τη Λευκωσία, και εξυπηρετώ πελάτες σε όλη την Κύπρο, στα Ελληνικά και στα Αγγλικά. Πιστεύω ότι η ασφάλιση δεν είναι απλώς ένα προϊόν· είναι ένα εργαλείο για να σχεδιάσει κανείς με ηρεμία το μέλλον του.' if el else 'I have been an Insurance Advisor since 2024. I am based in Nicosia and work with clients across Cyprus, in Greek and English. I believe insurance is not just a product; it is a way to plan your future calmly.'}</p>
<p>{'Για μένα κάθε πελάτης είναι ξεχωριστός. Ξεκινάμε από τις δικές σας ανάγκες και προχωράμε μόνο όταν όλα είναι ξεκάθαρα.' if el else 'Every client is different. We start from your needs and only go ahead once everything is clear.'}</p>
<p><a class="btn btn-ghost" href="{url('about', lang)}">{'Περισσότερα για μένα και ένα σύντομο βίντεο' if el else 'More about me, and a short video'}</a></p>
</div>
<blockquote class="quote quote--card">{L(T['motto'], lang)}<span>{'Μαζί μπορούμε να χτίσουμε ένα ασφαλές και σταθερό αύριο.' if el else 'Together we can build a safe and steady future.'}</span></blockquote>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Χρήσιμοι οδηγοί' if el else 'Helpful guides'}</h2>
<p class="lead">{'Σύντομες απαντήσεις στις ερωτήσεις που ακούω πιο συχνά, και λίστες για τις μεγάλες αλλαγές της ζωής.' if el else 'Short answers to the questions I hear most often, and lists for the big changes in life.'}</p></div>
{guides}
</div></section>

<section class="section tint"><div class="wrap callback-wrap">
<div class="callback-side"><hr class="rule"><h2>{'Προτιμάτε να σας καλέσω;' if el else 'Would you rather I called you?'}</h2>
<p>{'Αν δεν σας βολεύει να τηλεφωνήσετε τώρα, αφήστε μου όνομα και τηλέφωνο. Σας καλώ εγώ το πρωί, το μεσημέρι ή το απόγευμα, όπως σας βολεύει.' if el else 'If it is not a good moment to phone, leave me your name and number. I will call you in the morning, at midday or in the afternoon, whichever suits you.'}</p></div>
{callback_form(lang, heading=False)}
</div></section>
''' + cta_band(lang) + callback_script() + foot(lang)

def page_about(lang):
    el = lang == 'el'
    title = 'Σχετικά με τον Γιάννη Φαραζή, Ασφαλιστικό Σύμβουλο' if el else 'About Giannis Farazis, Insurance Advisor'
    desc = 'Ασφαλιστικός Σύμβουλος από το 2024, με βάση τη Λευκωσία, για πελάτες σε όλη την Κύπρο, στα Ελληνικά και Αγγλικά.' if el else 'Insurance Advisor since 2024, based in Nicosia, working with clients across Cyprus in Greek and English.'
    facts = [
        ('Ιδιότητα' if el else 'Role', L(T['role'], lang)),
        ('Στις ασφάλειες από' if el else 'In insurance since', '2024'),
        ('Βάση' if el else 'Based in', 'Λευκωσία' if el else 'Nicosia'),
        ('Εξυπηρέτηση' if el else 'Clients', 'Σε όλη την Κύπρο' if el else 'Across Cyprus'),
        ('Γλώσσες' if el else 'Languages', 'Ελληνικά και Αγγλικά' if el else 'Greek and English'),
        ('Τηλέφωνο' if el else 'Phone', f'<a href="tel:{TEL}">{PHONE}</a>'),
        ('LinkedIn', f'<a href="{LINKEDIN}" rel="noopener">Giannis Farazis</a>'),
    ]
    fl = ''.join(f'<li><span>{a}</span><span>{b}</span></li>' for a, b in facts)
    meet = explainer('meet-giannis', lang, 'explainer--wide', 'alt')
    meet_band = (f'<section class="section section--film"><div class="wrap"><div class="section-head"><hr class="rule"><h2>{"Μια σύντομη γνωριμία" if el else "A short introduction"}</h2></div>{meet}</div></section>'
                 if meet else '')
    body = ('''<p class="lead">Ονομάζομαι Γιάννης Φαραζής και είμαι Ασφαλιστικός Σύμβουλος από το 2024.</p>
<p>Δουλεύω με βάση τη Λευκωσία και εξυπηρετώ οικογένειες, εργαζόμενους, αυτοαπασχολούμενους και επιχειρήσεις σε όλη την Κύπρο, στα Ελληνικά και στα Αγγλικά.</p>
<p>Ασχολούμαι με την προστασία της οικογένειας και του εισοδήματος, την ιατροφαρμακευτική κάλυψη, τη σύνταξη, την αποταμίευση και τις σπουδές των παιδιών. Στόχος μου είναι κάθε πελάτης να έχει λύσεις που καλύπτουν πραγματικές ανάγκες και να καταλαβαίνει ακριβώς τι υπογράφει.</p>
<p>Πιστεύω ότι η ασφάλιση είναι ένα εργαλείο οικονομικού σχεδιασμού και όχι ένα απλό προϊόν. Δουλεύω με διαφάνεια και υπευθυνότητα, και μένω δίπλα στους πελάτες μου και μετά την υπογραφή: στις αλλαγές της ζωής τους και όταν χρειαστεί μια αποζημίωση.</p>
<blockquote class="quote">Μαζί σου, κάθε στιγμή.<span>Μαζί μπορούμε να χτίσουμε ένα ασφαλές και σταθερό αύριο.</span></blockquote>''' if el else '''<p class="lead">My name is Giannis Farazis and I have been an Insurance Advisor since 2024.</p>
<p>I am based in Nicosia and work with families, employees, the self-employed and businesses across Cyprus, in Greek and English.</p>
<p>I help with protecting your family and income, health cover, retirement, savings and your children’s education. My aim is for every client to have cover that meets real needs, and to understand exactly what they are signing.</p>
<p>I see insurance as a tool for financial planning, not just a product. I work openly and responsibly, and I stay with my clients after they sign: as their lives change, and when they need to make a claim.</p>
<blockquote class="quote">With you, every moment.<span>Together we can build a safe and steady future.</span></blockquote>''')
    return head(lang, 'about', title, desc) + f'''
<section class="about-hero on-dark"><div class="wrap">
<div><p class="hero__role">{L(T['role'], lang)}</p><h1>{L(T['name'], lang)}</h1><p class="hero__lead">{L(T['where'], lang)}</p>{actions(lang)}</div>
<figure class="portrait portrait--sm">{LINES}{portrait('Ο Γιάννης Φαραζής' if el else 'Giannis Farazis', eager=True, n='2')}</figure>
</div></section>
<section class="section"><div class="wrap about-body">
<div class="prose">{body}</div>
<aside><h2 class="aside-title">{'Με μια ματιά' if el else 'At a glance'}</h2><ul class="facts">{fl}</ul></aside>
</div></section>
{meet_band}
<section class="section tint"><div class="wrap"><div class="section-head"><hr class="rule"><h2>{'Πώς θέλω να δουλεύουμε' if el else 'How I like to work'}</h2></div>{values_grid(lang)}</div></section>
''' + cta_band(lang) + foot(lang)

def page_solutions(lang):
    el = lang == 'el'
    title = 'Ασφαλιστικές λύσεις: ζωή, υγεία, σύνταξη, αποταμίευση' if el else 'Insurance solutions: life, health, retirement, savings'
    desc = ('Ασφάλεια ζωής, υγείας και ατυχήματος, σύνταξη, αποταμίευση, σπουδές, δάνειο, προστασία επιχείρησης, ομαδικά σχέδια, ξένοι κάτοικοι, επανεξέταση.' if el
            else 'Life, health and accident cover, retirement, savings, education, loans, business protection, group plans, expats and policy reviews in Cyprus.')
    jump = '<nav class="jump" aria-label="' + ('Οι λύσεις' if el else 'Solutions') + '">' + ''.join(f'<a href="#{sid}">{L(t, lang)}</a>' for sid, _, t, *_ in SOLUTIONS) + '</nav>'
    rows = ''
    for i, (sid, img, t, s, lng, inc, q) in enumerate(SOLUTIONS):
        fm = explainer(film_of(FILM_OF.get(sid)), lang)   # the subject's narrated film; otherwise its icon (its photo is on the home page)
        media = fm or icon_panel(TOPIC_ICON.get(sid, 't-review'), 'icon-panel--wide')
        rows += f'''<article class="sol{' is-reverse' if i % 2 else ''}{' has-film' if fm else ''}" id="{sid}">
{media}
<div><h2>{L(t, lang)}</h2><p class="sol__short">{L(s, lang)}</p><p>{L(lng, lang)}</p>
<h3>{'Μπορεί να περιλαμβάνει' if el else 'It can include'}</h3>
<ul class="ticks">{''.join(f'<li>{ICON["check"]}{L(x, lang)}</li>' for x in inc)}</ul>
<p class="ask"><span>{'Η ερώτηση που ξεκινάμε' if el else 'Where we start'}</span>{L(q, lang)}</p>
{(f'<p><a href="{url("employers", lang)}">{L(T["nav"]["employers"], lang)}</a>{ICON["arrow"]}</p>') if sid == 'group' else ''}
</div></article>'''
    note = ('Κάθε πρόταση βασίζεται στους όρους του συγκεκριμένου συμβολαίου. Οι καλύψεις έχουν όρια, εξαιρέσεις και, όπου ισχύει, περιόδους αναμονής, που τα βλέπουμε μαζί πριν υπογράψετε. Οι αποδόσεις των επενδυτικών προγραμμάτων δεν είναι εγγυημένες, και η φορολογική έκπτωση εξαρτάται από την προσωπική σας περίπτωση.' if el
            else 'Every proposal is based on the terms of the specific policy. Cover has limits, exclusions and, where they apply, waiting periods, which we go through together before you sign. Returns on investment-linked plans are not guaranteed, and tax relief depends on your own circumstances.')
    return head(lang, 'solutions', title, desc) + page_head(L(T['nav']['solutions'], lang),
        'Έντεκα ανάγκες που βλέπουμε μαζί. Ξεκινάμε πάντα από μια απλή ερώτηση.' if el else 'Eleven needs we look at together. We always start with one simple question.', None, '', 'film-solutions', lang) + f'''
<section class="section section--tight"><div class="wrap">{jump}{rows}<p class="note">{note}</p></div></section>''' + cta_band(lang) + foot(lang)

def page_how(lang):
    el = lang == 'el'
    title = 'Πώς δουλεύω: από την πρώτη συζήτηση στην αποζημίωση' if el else 'How I work: from the first conversation to a claim'
    desc = 'Πρώτη συζήτηση, ανάλυση αναγκών, πρόταση με απλά λόγια και υποστήριξη μετά την υπογραφή. Τι να έχετε έτοιμο πριν μιλήσουμε.' if el else 'A first conversation, a look at your needs, a proposal in plain words, and support after you sign. What to have ready before we talk.'
    prep = (['Τι θέλετε να προστατεύσετε περισσότερο: οικογένεια, εισόδημα, υγεία, σπίτι ή σύνταξη.', 'Αν υπάρχει δάνειο ή άλλη μεγάλη υποχρέωση, και για πόσα χρόνια.', 'Τα συμβόλαια που ήδη έχετε: τουλάχιστον το είδος, την εταιρεία και το ασφάλιστρο.', 'Ένα κατά προσέγγιση μηνιαίο εισόδημα και τα βασικά έξοδα του σπιτιού.'] if el
            else ['What you most want to protect: family, income, health, home or retirement.', 'Whether there is a loan or other big commitment, and for how many years.', 'The policies you already have: at least the type, the insurer and the premium.', 'A rough monthly income and the household’s main costs.'])
    rows = ''.join(f'''<article class="sol{' is-reverse' if i % 2 else ''}"><figure>{photo(img, lang, sizes='(max-width: 860px) 100vw, 520px')}</figure>
<div><p class="sol__step">{('Βήμα ' if el else 'Step ')}{i + 1}</p><h2>{L(t, lang)}</h2><p>{L(d, lang)}</p></div></article>''' for i, (img, t, d) in enumerate(STEPS))
    return head(lang, 'how', title, desc) + page_head(L(T['nav']['how'], lang), 'Τέσσερα βήματα, χωρίς βιασύνη και χωρίς ψιλά γράμματα.' if el else 'Four steps, with no rush and no small print.', None, '', 'film-how', lang) + f'''
<section class="section section--tight"><div class="wrap">{rows}</div></section>
{film_band(lang, 'fg-how', 'Πώς δουλεύω, σε ένα σύντομο βίντεο' if el else 'How I work, in a short film')}
<section class="section tint"><div class="wrap split split--wide">
<figure class="split__img">{photo('how-prepare', lang, sizes='(max-width: 860px) 100vw, 560px')}</figure>
<div><hr class="rule"><h2>{'Πριν μιλήσουμε' if el else 'Before we talk'}</h2>
<p>{'Δεν χρειάζεται να έχετε τα πάντα έτοιμα. Αν όμως σκεφτείτε από πριν τα παρακάτω, η συζήτηση θα είναι πιο σύντομη και πιο χρήσιμη.' if el else 'You do not need everything ready. But if you think about these beforehand, the conversation will be shorter and more useful.'}</p>
<ul class="ticks">{''.join(f'<li>{ICON["check"]}{x}</li>' for x in prep)}</ul>
<p><a href="{url('first', lang)}">{'Η πρώτη συνάντηση: τι να φέρετε' if el else 'Your first meeting: what to bring'}</a>{ICON['arrow']}</p>
<p><a href="{url('faq', lang)}">{L(T['nav']['faq'], lang)}</a>{ICON['arrow']}</p>
<p class="note">{'Μη στέλνετε ιατρικά στοιχεία ή αριθμούς λογαριασμών μέσω της φόρμας. Αν χρειαστεί, τα συζητάμε με ασφαλή τρόπο.' if el else 'Please do not send medical details or account numbers through the form. If needed, we discuss them securely.'}</p>
</div></div></section>''' + cta_band(lang) + foot(lang)

# free checklists (ideas track 7): texts in tools/checklists.py, A4 PDFs made by tools/make_pdfs.py into assets/pdf/
import sys as _sys
_sys.path.insert(0, os.path.join(ROOT, 'tools'))
from checklists import CHECKLISTS, pdf_name

def checklists_section(lang):
    el = lang == 'el'
    pl = 'ru' if RENDER['ru'] else lang   # the Russian page links the Russian PDFs
    items = ''
    for cid, stem, title, desc, *_ in CHECKLISTS:
        f = pdf_name(stem, pl)
        size = os.path.getsize(os.path.join(ROOT, 'assets', 'pdf', f)) if os.path.exists(os.path.join(ROOT, 'assets', 'pdf', f)) else 0
        items += (f'<li><a class="dl" href="/assets/pdf/{f}" download><span class="dl__ico">{ICON["clear"]}</span><span><b>{esc(title["en" if lang == "en" else "el"])}</b>'
                  f'<small>{esc(desc["en" if lang == "en" else "el"])}</small><small class="dl__meta">PDF · A4 · {max(1, round(size / 1024))} KB</small></span></a></li>')
    return f'''<section class="section tint" id="checklists"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Δωρεάν λίστες ελέγχου' if el else 'Free checklists'}</h2>
<p class="lead">{'Τέσσερις σελίδες για εκτύπωση ή για το κινητό, με απλά λόγια. Χωρίς εγγραφή και χωρίς e-mail.' if el else 'Four pages to print or keep on your phone, in plain words. No sign-up and no e-mail.'}</p></div>
<ul class="dls">{items}</ul>
{checklist_films(lang)}
</div></section>'''

def checklist_films(lang):
    """the short films that go with the checklists (tools/add_explainers.py), in a row under the PDFs"""
    films = ''.join(f'<li>{f}</li>' for f in (explainer(FILM_OF_CHECKLIST.get(stem, ''), lang) for _, stem, *_ in CHECKLISTS) if f)
    if not films: return ''
    el = lang == 'el'
    return f'<h3 class="films-title">{"Τρία σύντομα βίντεο για τις λίστες" if el else "Three short films that go with the lists"}</h3><ul class="films">{films}</ul>'

def page_guides(lang):
    el = lang == 'el'
    title = 'Χρήσιμοι οδηγοί ασφάλισης για την Κύπρο' if el else 'Helpful insurance guides for Cyprus'
    desc = 'Πόση ασφάλεια ζωής χρειάζεστε, ΓεΣΥ και ιδιωτικό σχέδιο υγείας, και πότε να επανεξετάσετε τα συμβόλαιά σας.' if el else 'How much life cover you need, GESY and private health plans, and when to review your policies.'
    body = ''.join(f'''<article class="guide" id="{gid}"><figure>{photo(img, lang, sizes='(max-width: 860px) 100vw, 420px')}</figure><div class="prose"><h2>{L(t, lang)}</h2><p class="sol__short">{L(s, lang)}</p>{L(b, lang)}</div></article>''' for gid, img, t, s, b in GUIDES)
    more = (f'<p>Για περισσότερους οδηγούς και δωρεάν υπολογιστές, δείτε το <a href="{AVRASTRO}/guides/" rel="noopener">AVRASTRO</a>, την ενημερωτική πλατφόρμα που δημιούργησα.</p>' if el
            else f'<p>For more guides and free calculators, see <a href="{AVRASTRO}/en/guides/" rel="noopener">AVRASTRO</a>, the information platform I created.</p>')
    src = ('Πηγή για τη φορολογική έκπτωση: PwC Worldwide Tax Summaries – Cyprus (Οκτώβριος 2026). Οι οδηγοί είναι γενική ενημέρωση και όχι εξατομικευμένη συμβουλή.' if el
           else 'Source for tax relief: PwC Worldwide Tax Summaries – Cyprus (October 2026). The guides are general information, not personal advice.')
    return head(lang, 'guides', title, desc) + page_head(L(T['nav']['guides'], lang), 'Σύντομες απαντήσεις στις ερωτήσεις που ακούω πιο συχνά.' if el else 'Short answers to the questions I hear most often.', None, '', 'film-guides', lang,
        extra=print_button(lang)) + f'''
<section class="section section--tight"><div class="wrap">{body}<div class="prose"><p class="note">{src}</p>{more}</div></div></section>''' + checklists_section(lang) + f'''
<section class="section no-print"><div class="wrap"><div class="section-head"><hr class="rule"><h2>{'Και ακόμη' if el else 'Also useful'}</h2></div>
{link_cards(lang, [('list', L(T['nav']['events'], lang), 'Γάμος, παιδί, σπίτι, νέα δουλειά, μετακόμιση στην Κύπρο, σύνταξη: τι να ελέγξετε σε κάθε περίπτωση.' if el else 'Marriage, a child, a home, a new job, moving to Cyprus, retirement: what to check in each case.', url('events', lang)),
                   ('question', L(T['nav']['faq'], lang), 'Η πρώτη συνάντηση, το κόστος, οι αποζημιώσεις και τα στοιχεία σας.' if el else 'The first meeting, costs, claims and your details.', url('faq', lang))])}
</div></section>''' + cta_band(lang) + foot(lang)

def page_contact(lang):
    title = {'el': 'Επικοινωνία: Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος', 'en': 'Contact Giannis Farazis, Insurance Advisor'}[lang]
    desc = {'el': 'Κινητό +357 97 840941, γραφείο +357 22 124867, WhatsApp ή φόρμα επικοινωνίας. Εξυπηρέτηση σε όλη την Κύπρο, Ελληνικά και Αγγλικά.', 'en': 'Mobile +357 97 840941, office +357 22 124867, WhatsApp or the contact form. Serving clients across Cyprus, in Greek and English.'}[lang]
    topics = {'el': ['Ασφάλεια ζωής', 'Υγεία', 'Ατύχημα', 'Σύνταξη', 'Αποταμίευση / επενδυτικά', 'Παιδί και σπουδές', 'Προστασία δανείου', 'Επιχείρηση / ομαδικά', 'Επανεξέταση συμβολαίων', 'Κάτι άλλο'],
              'en': ['Life insurance', 'Health', 'Accident', 'Retirement', 'Savings / investment-linked', 'Children and education', 'Loan protection', 'Business / group', 'Policy review', 'Something else']}[lang]
    opts = ''.join(f'<option>{esc(t)}</option>' for t in topics)
    el = lang == 'el'
    return head(lang, 'contact', title, desc) + page_head(L(T['nav']['contact'], lang), 'Μια πρώτη συζήτηση, χωρίς δέσμευση.' if el else 'A first conversation, with no commitment.', lang=lang) + f'''
<section class="section"><div class="wrap contact-grid">
<div class="card-id on-dark">
<h2>{L(T['name'], lang)}</h2>
<p class="aff">{'Ασφαλιστικός Σύμβουλος — Eurolife' if el else 'Insurance Advisor — Eurolife'}</p>
<p>{'Εξυπηρέτηση Παγκύπρια | Ελληνικά &amp; Αγγλικά' if el else 'Serving clients across Cyprus | Greek &amp; English'}</p>
<dl>
<dt>{'Κινητό (Επαγγελματικό)' if el else 'Business mobile'}</dt><dd><a href="tel:{TEL}">{PHONE}</a></dd>
<dt>{'Γραφείο' if el else 'Office'}</dt><dd><a href="tel:{OFFICE_TEL}">{OFFICE}</a></dd>
<dt>WhatsApp</dt><dd><a href="{WHATSAPP}" rel="noopener">{PHONE}</a></dd>
<dt>{'Διεύθυνση' if el else 'Address'}</dt><dd>{'Λεωφόρος Στροβόλου 124Γ, 5ος όροφος, Λευκωσία' if el else '124C Strovolou Avenue, 5th floor, Nicosia'}</dd>
<dt>LinkedIn</dt><dd><a href="{LINKEDIN}" rel="noopener">Giannis Farazis</a></dd>
</dl>
{actions(lang)}
</div>
<div>
<h2>{'Αφήστε τα στοιχεία σας' if el else 'Leave your details'}</h2>
<p>{'Θα σας καλέσω για μια προσωπική ενημέρωση.' if el else 'I will call you back for a personal conversation.'}</p>
<form class="form" id="enquiry" action="{ENQUIRY}" method="post" novalidate data-lang="{lang}">
<div class="row">
<label>{'Ονοματεπώνυμο' if el else 'Full name'}<input name="name" autocomplete="name" required maxlength="120"></label>
<label>{'Τηλέφωνο' if el else 'Phone'}<input name="phone" type="tel" autocomplete="tel" inputmode="tel" maxlength="40"></label>
</div>
<label>E-mail <span class="hint">{'(προαιρετικό αν δώσατε τηλέφωνο)' if el else '(optional if you gave a phone number)'}</span><input name="email" type="email" autocomplete="email" maxlength="160"></label>
<label>{'Θέμα' if el else 'Topic'}<select name="topic">{opts}</select></label>
<label>{'Μήνυμα' if el else 'Message'} <span class="hint">{'Μη γράφετε ιατρικά στοιχεία ή αριθμούς λογαριασμών.' if el else 'Please do not include medical details or account numbers.'}</span><textarea name="message" maxlength="3000"></textarea></label>
<div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
<label class="check"><input type="checkbox" name="consent" required><span>{f'Συμφωνώ να επικοινωνήσει μαζί μου ο Γιάννης Φαραζής για αυτό το αίτημα. Δείτε την <a href="{url("privacy", lang)}">πολιτική απορρήτου</a>.' if el else f'I agree that Giannis Farazis may contact me about this request. See the <a href="{url("privacy", lang)}">privacy policy</a>.'}</span></label>
<div class="status" role="status" aria-live="polite"></div>
<button class="btn btn-primary" type="submit">{'Αποστολή' if el else 'Send'}</button>
</form>
</div>
</div></section>
<section class="section tint"><div class="wrap callback-wrap">
<div class="callback-side"><hr class="rule"><h2>{'Ή απλώς ζητήστε να σας καλέσω' if el else 'Or simply ask me to call you'}</h2>
<p>{'Χωρίς μήνυμα και χωρίς e-mail: μόνο όνομα, τηλέφωνο και πότε σας βολεύει.' if el else 'No message and no e-mail: just your name, your phone number and when suits you.'}</p></div>
{callback_form(lang, heading=False)}
</div></section>''' + callback_script() + foot(lang)

BOOKING_TOPICS = [('review', 'Ετήσια επανεξέταση', 'Annual review'), ('life', 'Ασφάλεια ζωής', 'Life cover'), ('health', 'Υγεία / ιατροφαρμακευτική', 'Health / medical'),
                  ('savings', 'Αποταμίευση', 'Savings'), ('pension', 'Σύνταξη', 'Retirement'), ('children', 'Παιδιά & σπουδές', 'Children & education'),
                  ('property', 'Κατοικία & δάνειο', 'Home & mortgage'), ('business', 'Επιχείρηση', 'Business'), ('claim', 'Αποζημίωση / απαίτηση', 'Claim'), ('other', 'Άλλο', 'Other')]
BOOKING_MODES = [('office', 'Στο γραφείο', 'At the office'), ('video', 'Βιντεοκλήση', 'Video call'), ('phone', 'Τηλεφωνικά', 'By phone')]
CALLBACK_TIMES = [('morning', 'Πρωί', 'Morning'), ('midday', 'Μεσημέρι', 'Midday'), ('afternoon', 'Απόγευμα', 'Afternoon')]

def callback_form(lang, topic='life', title=None, lead=None, heading=True):
    """«Πάρτε με τηλέφωνο» (ideas track 8, 14 Oct 2026): name, phone, when a call suits and a LIFE topic. Sent by
    assets/js/callback.js to avrastro.com's contact endpoint as a call-back request (CORS allow-list there, JSON, no
    cookies); it reaches the CRM inbox as a call task at that time of day. No e-mail asked. One per page."""
    el = lang == 'el'
    topics = ''.join(f'<option value="{k}"' + (' selected' if k == topic else '') + f'>{esc(a if el else b)}</option>' for k, a, b in BOOKING_TOPICS)
    times = ''.join(f'<label class="when__opt"><input type="radio" name="best_time" value="{k}"' + (' checked' if i == 0 else '') + f'><span>{esc(a if el else b)}</span></label>'
                    for i, (k, a, b) in enumerate(CALLBACK_TIMES))
    title = title or ('Πάρτε με τηλέφωνο' if el else 'Ask me to call you')
    lead = lead or ('Αφήστε όνομα και τηλέφωνο, πείτε μου πότε σας βολεύει, και σας καλώ εγώ. Χωρίς δέσμευση.' if el
                    else 'Leave your name and phone number, tell me when suits you, and I will call you. No commitment.')
    consent = (f'Συμφωνώ να με καλέσει ο Γιάννης Φαραζής για αυτό το αίτημα. Το αίτημα καταχωρίζεται στο σύστημα του avrastro.com και στο σύστημα διαχείρισης πελατών του. Δείτε την <a href="{url("privacy", lang, "callback")}">πολιτική απορρήτου</a>.' if el
               else f'I agree that Giannis Farazis may call me about this request. The request is recorded in the avrastro.com system and in his client management system. See the <a href="{url("privacy", lang, "callback")}">privacy policy</a>.')
    top = f'<h2>{title}</h2>\n<p>{lead}</p>\n' if heading else ''
    return f'''<div class="callback" id="call-me">
{top}<form class="form" id="callback" novalidate data-api="{esc(BOOKING_API)}" data-lang="{lang}">
<div class="row">
<label>{'Όνομα' if el else 'Name'}<input name="name" autocomplete="name" required maxlength="120"></label>
<label>{'Τηλέφωνο' if el else 'Phone'}<input name="phone" type="tel" autocomplete="tel" inputmode="tel" required maxlength="40"></label>
</div>
<fieldset class="when"><legend>{'Πότε σας βολεύει;' if el else 'When suits you?'}</legend><div class="when__opts">{times}</div></fieldset>
<label>{'Θέμα' if el else 'Topic'}<select name="topic">{topics}</select></label>
<div class="hp" aria-hidden="true"><label>Leave empty<input name="vc_hp_x" tabindex="-1" autocomplete="off"></label></div>
<label class="check"><input type="checkbox" name="privacy" required><span>{consent}</span></label>
<noscript><p class="status err" style="display:block">{'Η φόρμα χρειάζεται JavaScript. Καλέστε στο' if el else 'This form needs JavaScript. Please call'} <a href="tel:{TEL}">{PHONE}</a>.</p></noscript>
<div class="status" role="status" aria-live="polite"></div>
<button class="btn btn-primary" type="submit">{ICON['phone']}{'Καλέστε με' if el else 'Call me back'}</button>
</form>
<div class="form callback-done" data-callback-done hidden tabindex="-1"><h3>{'Το αίτημα στάλθηκε' if el else 'Your request has been sent'}</h3>
<p>{'Ευχαριστώ. Θα σας καλέσω στο τηλέφωνο που δώσατε, στο διάστημα που διαλέξατε ή το συντομότερο δυνατό.' if el else 'Thank you. I will call you on the number you gave, in the part of the day you chose or as soon as I can.'}</p></div>
</div>'''

def callback_script():
    return f'<script src="/assets/js/callback.js?v={ASSET_V}" defer></script>'

# «Έλεγχος αναγκών» (14 Oct 2026 features): six short questions before the first meeting. Optional, no medical questions,
# nothing stored in the browser: booking.js adds the answers to the note that goes with the booking request (in English
# on the Russian page, which the advisor reads), so the first meeting starts from them. Life business only.
NEEDS = [
    ('household', 'radio', {'el': 'Το νοικοκυριό σας', 'en': 'Your household'}, [
        ('single', 'Ζω μόνος / μόνη', 'I live alone'), ('couple', 'Ζευγάρι χωρίς παιδιά', 'A couple without children'),
        ('family', 'Ζευγάρι με παιδιά', 'A couple with children'), ('parent', 'Μονογονεϊκή οικογένεια', 'A single parent')]),
    ('work', 'radio', {'el': 'Η δουλειά σας', 'en': 'Your work'}, [
        ('employee', 'Μισθωτός / μισθωτή', 'Employee'), ('self', 'Αυτοαπασχολούμενος / αυτοαπασχολούμενη', 'Self-employed'),
        ('owner', 'Ιδιοκτήτης επιχείρησης', 'Business owner'), ('retired', 'Συνταξιούχος', 'Retired'), ('other', 'Κάτι άλλο', 'Something else')]),
    ('loan', 'radio', {'el': 'Δάνειο', 'en': 'Loans'}, [
        ('mortgage', 'Έχω στεγαστικό', 'I have a mortgage'), ('newmortgage', 'Θα πάρω στεγαστικό σύντομα', 'I am about to take out a mortgage'),
        ('other', 'Έχω άλλο δάνειο', 'I have another loan'), ('none', 'Δεν έχω δάνειο', 'I have no loan')]),
    ('have', 'checkbox', {'el': 'Τι έχετε ήδη', 'en': 'What you already have'}, [
        ('life', 'Ασφάλεια ζωής', 'Life cover'), ('health', 'Σχέδιο υγείας', 'A health plan'), ('provident', 'Ταμείο προνοίας στη δουλειά', 'A provident fund at work'),
        ('pension', 'Συνταξιοδοτικό ή αποταμιευτικό σχέδιο', 'A pension or savings plan'), ('none', 'Τίποτα από αυτά', 'None of these'), ('unsure', 'Δεν είμαι σίγουρος / σίγουρη', 'I am not sure')]),
    ('goals', 'checkbox', {'el': 'Τι σας απασχολεί περισσότερο (έως τρία)', 'en': 'What matters most to you (up to three)'}, [
        ('family', 'Να προστατεύσω την οικογένεια', 'Protecting my family'), ('income', 'Το εισόδημα, αν δεν μπορώ να δουλέψω', 'My income, if I cannot work'),
        ('health', 'Υγεία και νοσηλεία', 'Health and hospital care'), ('retirement', 'Η σύνταξη', 'Retirement'), ('savings', 'Αποταμίευση για έναν στόχο', 'Saving towards a goal'),
        ('studies', 'Οι σπουδές των παιδιών', 'The children’s studies'), ('mortgage', 'Το στεγαστικό', 'The mortgage'), ('review', 'Έλεγχος όσων ήδη έχω', 'A check of what I already have')]),
    ('when', 'radio', {'el': 'Πότε θα θέλατε να ξεκινήσετε', 'en': 'When you would like to start'}, [
        ('soon', 'Το συντομότερο', 'As soon as possible'), ('months', 'Τους επόμενους μήνες', 'In the next few months'), ('info', 'Απλώς ενημερώνομαι', 'I am just finding out')]),
]

def needs_check(lang):
    el = lang == 'el'
    qs = ''
    for qid, kind, q, opts in NEEDS:
        o = ''.join(f'<label class="opt"><input type="{kind}" name="nc_{qid}" value="{k}" data-en="{esc(b)}"><span>{esc(a if el else b)}</span></label>' for k, a, b in opts)
        qs += f'<fieldset class="needs__q" data-q="{qid}" data-q-en="{esc(q["en"])}" data-kind="{kind}"><legend>{q["el"] if el else q["en"]}</legend><div class="opts">{o}</div></fieldset>'
    return f'''<details class="needs" id="needs" data-needs data-label="{'Έλεγχος αναγκών' if el else 'Needs check'}">
<summary><span class="needs__ico">{ICON['list']}</span><span><b>{'Σύντομος έλεγχος αναγκών' if el else 'A short needs check'}</b><small>{'Προαιρετικό · περίπου ένα λεπτό · οι απαντήσεις πηγαίνουν μαζί με το αίτημα' if el else 'Optional · about a minute · your answers go with the request'}</small></span></summary>
<div class="needs__body">
<p class="hint">{'Έξι σύντομες ερωτήσεις, ώστε η πρώτη συνάντηση να ξεκινήσει από ό,τι σας αφορά. Χωρίς ερωτήσεις υγείας και χωρίς ποσά.' if el else 'Six short questions, so that the first meeting starts from what matters to you. No health questions and no amounts.'}</p>
{qs}
<div class="needs__preview" data-needs-preview hidden><b>{'Θα σταλεί μαζί με το αίτημα:' if el else 'This will be sent with your request:'}</b><p data-needs-text></p></div>
</div></details>'''

def page_booking(lang):
    """The same calendar as avrastro.com (booking.js). Without JavaScript: a link to the booking page on avrastro.com."""
    el = lang == 'el'
    title = {'el': 'Κλείστε ραντεβού με τον Γιάννη Φαραζή, Ασφαλιστικό Σύμβουλο', 'en': 'Book an appointment with Giannis Farazis, Insurance Advisor'}[lang]
    desc = {'el': 'Διαλέξτε μέρα και ώρα από τις πραγματικές ελεύθερες ώρες: στο γραφείο στη Λευκωσία, με βιντεοκλήση ή τηλεφωνικά. Χωρίς δέσμευση.',
            'en': 'Choose a day and time from the real free times: at the office in Nicosia, by video call or by phone. No commitment.'}[lang]
    topics = ''.join(f'<option value="{k}">{esc(a if el else b)}</option>' for k, a, b in BOOKING_TOPICS)
    modes = ''.join(f'<option value="{k}">{esc(a if el else b)}</option>' for k, a, b in BOOKING_MODES)
    fallback = AVRASTRO + ('/en' if not el else '') + '/citizen-booking/'
    steps = (['Διαλέγετε θέμα, τρόπο, μέρα και ώρα.', 'Λαμβάνετε αμέσως e-mail ότι το αίτημα παραλήφθηκε.', 'Το επιβεβαιώνω και σας έρχεται e-mail με όλες τις λεπτομέρειες και υπενθύμιση την προηγούμενη μέρα.']
             if el else ['Choose a topic, a way to meet, a day and a time.', 'You receive an e-mail at once that the request was received.', 'I confirm it and you receive an e-mail with every detail, and a reminder the day before.'])
    return head(lang, 'booking', title, desc) + page_head(L(T['nav']['booking'], lang), 'Μια πρώτη συζήτηση, χωρίς δέσμευση, την ώρα που σας βολεύει.' if el else 'A first conversation, with no commitment, at a time that suits you.', lang=lang) + f'''
<section class="section"><div class="wrap contact-grid booking-grid">
<div class="booking-how">
<h2>{'Πώς γίνεται' if el else 'How it works'}</h2>
<ol class="steps-mini">{''.join(f'<li>{esc(x)}</li>' for x in steps)}</ol>
{explainer('fg-callback', lang, 'explainer--side')}
<p class="booking-needs">{ICON['list']}<span>{'Στη φόρμα θα βρείτε και έναν <a href="#needs" data-open-needs>σύντομο έλεγχο αναγκών</a>: έξι ερωτήσεις, προαιρετικές, που πηγαίνουν μαζί με το αίτημα.' if el else 'The form also has a <a href="#needs" data-open-needs>short needs check</a>: six optional questions that go with your request.'}</span></p>
<p>{'Η συνάντηση διαρκεί περίπου' if el else 'The meeting takes about'} <b><span data-minutes>45</span> {'λεπτά' if el else 'minutes'}</b>. {'Οι ώρες είναι ώρα Κύπρου.' if el else 'Times are Cyprus time.'}</p>
<p><a href="{url('first', lang)}">{'Πώς γίνεται η πρώτη συνάντηση και τι να φέρετε' if el else 'How the first meeting works and what to bring'}</a>{ICON['arrow']}</p>
<p class="hint">{'Το ημερολόγιο είναι το ίδιο με εκείνο του avrastro.com: μια ώρα που κλείνεται εδώ δεν μπορεί να κλειστεί αλλού.' if el else 'The calendar is the same as on avrastro.com: a time booked here cannot be booked anywhere else.'}</p>
<p>{'Προτιμάτε να μιλήσουμε πρώτα;' if el else 'Would you rather talk first?'}</p>
{actions(lang, book=False)}
</div>
<div id="booking" class="booking" data-api="{esc(BOOKING_API)}" data-lang="{lang}">
<noscript><p class="status err" style="display:block">{'Για την online κράτηση χρειάζεται JavaScript.' if el else 'Online booking needs JavaScript.'} <a href="{fallback}">{'Κλείστε ραντεβού στο avrastro.com' if el else 'Book on avrastro.com'}</a></p></noscript>
<form class="form" novalidate>
<div class="row">
<label>{'Θέμα' if el else 'Topic'}<select name="topic">{topics}</select></label>
<label>{'Τρόπος' if el else 'Type'}<select name="mode">{modes}</select></label>
</div>
<fieldset class="pick"><legend>{'Διαλέξτε ημέρα' if el else 'Choose a day'}</legend><div class="chips" data-days aria-live="polite"></div><button class="btn btn-link more-days" type="button" data-more hidden>{'Περισσότερες ημέρες' if el else 'More days'}</button></fieldset>
<fieldset class="pick"><legend>{'Διαλέξτε ώρα' if el else 'Choose a time'}</legend><div class="chips chips--time" data-slots aria-live="polite"></div></fieldset>
<div class="row">
<label>{'Ονοματεπώνυμο' if el else 'Full name'}<input name="name" autocomplete="name" required maxlength="120"></label>
<label><span>E-mail <span class="hint">{'(εκεί έρχεται η επιβεβαίωση)' if el else '(the confirmation is sent there)'}</span></span><input name="email" type="email" autocomplete="email" required maxlength="160"></label>
</div>
<label><span>{'Τηλέφωνο' if el else 'Phone'} <span class="hint">{'(προαιρετικό)' if el else '(optional)'}</span></span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" maxlength="40"></label>
{needs_check(lang)}
<label><span>{'Τι θα θέλατε να συζητήσουμε;' if el else 'What would you like to discuss?'} <span class="hint">{'Προαιρετικό. Μη γράφετε ιατρικά στοιχεία.' if el else 'Optional. Please do not include medical details.'}</span></span><textarea name="note" maxlength="1500"></textarea></label>
<div class="hp" aria-hidden="true"><label>Leave empty<input name="vc_hp_x" tabindex="-1" autocomplete="off"></label></div>
<label class="check"><input type="checkbox" name="privacy" required><span>{f'Διάβασα την <a data-privacy href="{AVRASTRO}/privacy/" rel="noopener">Πολιτική απορρήτου</a> και αποδέχομαι τους <a data-terms href="{AVRASTRO}/terms/" rel="noopener">Όρους χρήσης</a> του συστήματος ραντεβού AVRASTRO. Το αίτημα πηγαίνει στον Γιάννη Φαραζή και μπορεί να καταχωριστεί στο σύστημα διαχείρισης πελατών του.' if el else f'I have read the <a data-privacy href="{AVRASTRO}/en/privacy/" rel="noopener">Privacy notice</a> and accept the <a data-terms href="{AVRASTRO}/en/terms/" rel="noopener">Terms of use</a> of the AVRASTRO booking system. The request goes to Giannis Farazis and may be recorded in his client management system.'}</span></label>
<div class="status" role="status" aria-live="polite"></div>
<button class="btn btn-primary" type="submit">{'Αίτημα ραντεβού' if el else 'Request appointment'}</button>
</form>
<div class="form booking-done" data-done hidden tabindex="-1"><h2></h2><p class="booking-when" data-when></p><p data-body></p>
<p class="booking-first">{'Πριν έρθετε:' if el else 'Before we meet:'} <a href="{url('first', lang)}">{'πώς γίνεται η πρώτη συνάντηση και τι να φέρετε' if el else 'how the first meeting works and what to bring'}</a>.</p>
<p><button class="btn btn-ghost" type="button" data-again>…</button></p></div>
</div>
</div></section>
<script src="/assets/js/booking.js?v={ASSET_V}" defer></script>''' + foot(lang)

def page_first(lang):
    """Ideas track 10 (14 Oct 2026): how the first meeting works and what to bring. Linked from the booking page and its
    confirmation panel, and from How I work. Only what is true for every first meeting: about 45 minutes, nothing is
    signed, the same at the office, by video call or by phone."""
    el = lang == 'el'
    title = 'Η πρώτη συνάντηση: πώς γίνεται και τι να φέρετε' if el else 'Your first meeting: how it works and what to bring'
    desc = ('Περίπου 45 λεπτά, χωρίς να υπογράψετε τίποτα: τι συζητάμε στην πρώτη συνάντηση και ποια χαρτιά βοηθά να έχετε μαζί σας.' if el
            else 'About 45 minutes, and nothing to sign: what we talk about at the first meeting and which papers help to have with you.')
    facts = ([('45′', 'Περίπου 45 λεπτά', 'Αρκετός χρόνος για να γνωριστούμε και να δούμε τι χρειάζεστε, χωρίς βιασύνη.'),
              ('0', 'Δεν υπογράφετε τίποτα', 'Η πρώτη συνάντηση είναι γνωριμία και καταγραφή αναγκών. Δεν υπογράφεται αίτηση ούτε συμβόλαιο.'),
              ('3', 'Όπως σας βολεύει', 'Στο γραφείο στη Λευκωσία, με βιντεοκλήση ή τηλεφωνικά, στα Ελληνικά ή στα Αγγλικά.')] if el else
             [('45′', 'About 45 minutes', 'Enough time to get to know each other and look at what you need, with no rush.'),
              ('0', 'Nothing to sign', 'The first meeting is about getting to know you and noting what you need. No application or policy is signed.'),
              ('3', 'The way that suits you', 'At the office in Nicosia, by video call or by phone, in Greek or English.')])
    talk = (['Τι θέλετε να προστατεύσετε: την οικογένεια, το εισόδημα, την υγεία, ένα δάνειο, τη σύνταξη ή τις σπουδές των παιδιών.',
             'Τι έχετε ήδη: ασφάλειες, ταμείο προνοίας, αποταμιεύσεις και τι καλύπτει το ΓεΣΥ στη δική σας περίπτωση.',
             'Πού υπάρχουν κενά ή επικαλύψεις, με απλά λόγια.',
             'Τι ποσό είναι λογικό για εσάς κάθε μήνα, ώστε να μη γίνει βάρος.',
             'Τα επόμενα βήματα, αν θέλετε να συνεχίσουμε: τι θα ετοιμάσω και πότε θα τα δούμε μαζί.'] if el else
            ['What you want to protect: your family, your income, your health, a loan, your retirement or your children’s studies.',
             'What you already have: insurance, a provident fund, savings, and what GESY covers in your case.',
             'Where the gaps or overlaps are, in plain words.',
             'What amount each month is sensible for you, so that it does not become a burden.',
             'The next steps, if you want to go on: what I will prepare and when we will look at it together.'])
    bring = (['Τα συμβόλαια που ήδη έχετε (ζωής, υγείας, ατυχήματος, αποταμίευσης), ή έστω την εταιρεία, το είδος και το ασφάλιστρο.',
              'Αν έχετε στεγαστικό ή άλλο δάνειο: το υπόλοιπο, τη διάρκεια και τη μηνιαία δόση.',
              'Ένα κατά προσέγγιση μηνιαίο εισόδημα του νοικοκυριού και τα βασικά έξοδα.',
              'Αν συμμετέχετε σε ταμείο προνοίας ή σε ομαδικό σχέδιο της δουλειάς σας, ό,τι ενημέρωση έχετε γι’ αυτό.',
              'Τις ερωτήσεις σας, γραμμένες, για να μη ξεχαστεί καμία.'] if el else
             ['The policies you already have (life, health, accident, savings), or at least the insurer, the type and the premium.',
              'If you have a mortgage or another loan: the balance, the term and the monthly instalment.',
              'A rough monthly household income and the main costs.',
              'If you belong to a provident fund or a group plan at work, any statement you have for it.',
              'Your questions, written down, so that none is forgotten.'])
    nobring = (['Ιατρικούς φακέλους ή εξετάσεις: δεν χρειάζονται στην πρώτη συνάντηση.', 'Αριθμούς τραπεζικών λογαριασμών ή καρτών.', 'Πρωτότυπα έγγραφα: αρκούν αντίγραφα ή μια φωτογραφία στο κινητό.'] if el else
               ['Medical files or test results: they are not needed at the first meeting.', 'Bank account or card numbers.', 'Original documents: copies or a photo on your phone are enough.'])
    remote = ('Αν μιλάμε με βιντεοκλήση ή τηλεφωνικά, έχετε τα ίδια χαρτιά δίπλα σας. Δεν χρειάζεται να μου στείλετε τίποτα από πριν.' if el
              else 'If we talk by video call or by phone, have the same papers next to you. You do not need to send me anything beforehand.')
    after = ('Μετά τη συνάντηση αποφασίζετε εσείς αν θα συνεχίσουμε. Αν ναι, ετοιμάζω μια πρόταση με απλά λόγια, τι καλύπτει, τι δεν καλύπτει και πόσο κοστίζει, και τη βλέπουμε μαζί όποτε σας βολεύει. Μπορείτε να την πάρετε μαζί σας και να το σκεφτείτε όσο χρειάζεστε.' if el
             else 'After the meeting you decide whether to go on. If you do, I prepare a proposal in plain words, what it covers, what it does not and what it costs, and we go through it together whenever suits you. You can take it with you and think about it for as long as you need.')
    icons = ['clock', 'nosign', 'ways']
    fl = ''.join(f'<li><span class="meet-facts__ico">{ICON[icons[i]]}</span><h3>{t}</h3><p>{d}</p></li>' for i, (n, t, d) in enumerate(facts))
    ul = lambda xs: '<ul class="ticks">' + ''.join(f'<li>{ICON["check"]}{x}</li>' for x in xs) + '</ul>'
    xs = lambda xs: '<ul class="ticks ticks--no">' + ''.join(f'<li><span class="x" aria-hidden="true">×</span>{x}</li>' for x in xs) + '</ul>'
    book = f'<a class="btn btn-primary" href="{url("booking", lang)}">{ICON["cal"]}{L(T["nav"]["booking"], lang)}</a>'
    return head(lang, 'first', title, desc) + page_head(L(T['nav']['first'], lang),
        'Τι γίνεται στην πρώτη μας συνάντηση και τι βοηθά να έχετε μαζί σας.' if el else 'What happens at our first meeting, and what helps to have with you.', 'first-meeting', lang=lang,
        trail=[(L(T['nav']['how'], lang), url('how', lang))], extra=print_button(lang)) + f'''
<section class="section section--tight"><div class="wrap">
<ul class="meet-facts">{fl}</ul>
</div></section>
{film_band(lang, 'fg-first-meeting', 'Η πρώτη συνάντηση, σε ένα σύντομο βίντεο' if el else 'The first meeting, in a short film')}
<section class="section tint"><div class="wrap pair">
<article class="panel"><hr class="rule"><h2>{'Τι συζητάμε' if el else 'What we talk about'}</h2>{ul(talk)}</article>
<article class="panel"><hr class="rule"><h2>{'Τι να φέρετε' if el else 'What to bring'}</h2>
<p>{'Δεν χρειάζεται να έχετε τα πάντα. Ό,τι από τα παρακάτω βρείτε εύκολα κάνει τη συζήτηση πιο σύντομη και πιο χρήσιμη.' if el else 'You do not need everything. Whatever you find easily from the list below makes the conversation shorter and more useful.'}</p>
{ul(bring)}<p class="note">{remote}</p></article>
</div></section>
<section class="section"><div class="wrap pair">
<article class="panel panel--plain"><hr class="rule"><h2>{'Τι δεν χρειάζεται' if el else 'What you do not need'}</h2>{xs(nobring)}</article>
<article class="panel panel--plain"><hr class="rule"><h2>{'Μετά τη συνάντηση' if el else 'After the meeting'}</h2><p>{after}</p></article>
</div></section>
<section class="section tint no-print"><div class="wrap"><div class="needs-cta">
<span class="needs-cta__ico">{ICON['list']}</span>
<div><h2>{'Ένα λεπτό πριν από το ραντεβού' if el else 'One minute before you book'}</h2>
<p>{'Όταν κλείνετε ραντεβού online, μπορείτε να απαντήσετε σε έξι σύντομες, προαιρετικές ερωτήσεις: νοικοκυριό, δουλειά, δάνειο, τι έχετε ήδη και τι σας απασχολεί. Οι απαντήσεις έρχονται σε μένα μαζί με το αίτημα, ώστε η συνάντηση να ξεκινήσει από εκεί.' if el else 'When you book online, you can answer six short, optional questions: household, work, loans, what you already have and what matters to you. The answers reach me with your request, so the meeting starts from there.'}</p>
<div class="actions">{book}<a class="btn btn-ghost" href="{url('faq', lang)}">{ICON['question']}{L(T['nav']['faq'], lang)}</a></div></div>
</div></div></section>''' + cta_band(lang) + foot(lang)

# Ideas track 4 (14 Oct 2026): one page per city. Only what is true everywhere: the office is in Nicosia (124C Strovolou
# Avenue, 5th floor); meetings by video call or phone anywhere in Cyprus; in-person visits by arrangement. No invented
# local facts (no "local office", no local statistics, no testimonials). Each page has its own wording and structured
# data (Service with areaServed = the city).
OFFICE_EL = 'Λεωφόρος Στροβόλου 124Γ, 5ος όροφος, Λευκωσία'
OFFICE_EN = '124C Strovolou Avenue, 5th floor, Nicosia'
CITIES = [
    ('nicosia', 'lefkosia', 'nicosia', 'Λευκωσία', 'στη Λευκωσία', 'Nicosia', True,
     {'el': 'Το γραφείο μου είναι στη Λευκωσία, στη Λεωφόρο Στροβόλου. Εκεί γίνονται οι περισσότερες συναντήσεις από κοντά, και όποτε σας βολεύει μιλάμε και με βιντεοκλήση ή τηλεφωνικά.',
      'en': 'My office is in Nicosia, on Strovolou Avenue. Most in-person meetings happen there, and whenever it suits you we can also talk by video call or by phone.'},
     [{'el': 'Στο γραφείο', 'en': 'At the office'}, {'el': 'Ραντεβού στο γραφείο, στη Λεωφόρο Στροβόλου 124Γ, 5ος όροφος. Διαλέγετε μέρα και ώρα online ή με ένα τηλεφώνημα.', 'en': 'An appointment at the office, 124C Strovolou Avenue, 5th floor. Choose a day and time online or with a phone call.'}],
     [{'el': 'Με βιντεοκλήση ή τηλεφωνικά', 'en': 'By video call or phone'}, {'el': 'Αν δεν προλαβαίνετε να έρθετε, η ίδια συζήτηση γίνεται από το σπίτι ή τη δουλειά σας.', 'en': 'If you cannot make it to the office, the same conversation can happen from your home or workplace.'}],
     [{'el': 'Επίσκεψη κατόπιν συνεννόησης', 'en': 'A visit by arrangement'}, {'el': 'Αν χρειάζεται, π.χ. για μια επιχείρηση ή για κάποιον που δυσκολεύεται να μετακινηθεί, συνεννοούμαστε για συνάντηση στον δικό σας χώρο.', 'en': 'If needed, for example for a business or for someone who finds it hard to travel, we can arrange to meet at your place.'}]),
    ('limassol', 'lemesos', 'limassol', 'Λεμεσός', 'στη Λεμεσό', 'Limassol', False,
     {'el': 'Από τη Λεμεσό ο πιο απλός τρόπος είναι συχνά μια βιντεοκλήση: είναι το ίδιο ολοκληρωμένη συζήτηση, χωρίς τη διαδρομή μέχρι τη Λευκωσία. Αν θέλετε να συναντηθούμε από κοντά, το κανονίζουμε.',
      'en': 'From Limassol the simplest way is often a video call: it is just as complete a conversation, without the drive to Nicosia. If you would like to meet in person, we arrange it.'},
     [{'el': 'Πρώτα με βιντεοκλήση', 'en': 'Video call first'}, {'el': 'Η πρώτη συνάντηση, περίπου 45 λεπτά, γίνεται άνετα με βιντεοκλήση. Βλέπουμε μαζί τα συμβόλαια και τις ανάγκες σας στην οθόνη.', 'en': 'The first meeting, about 45 minutes, works well by video call. We look at your policies and needs together on screen.'}],
     [{'el': 'Τηλεφωνικά', 'en': 'By phone'}, {'el': 'Για μια σύντομη ερώτηση ή αν δεν σας βολεύει η κάμερα, μιλάμε απλώς στο τηλέφωνο.', 'en': 'For a quick question, or if a camera does not suit you, we simply talk on the phone.'}],
     [{'el': 'Από κοντά, κατόπιν συνεννόησης', 'en': 'In person, by arrangement'}, {'el': 'Στο γραφείο στη Λευκωσία όποτε περνάτε από εκεί, ή επίσκεψη στη Λεμεσό αφού το συνεννοηθούμε.', 'en': 'At the office in Nicosia whenever you are there, or a visit in Limassol once we have arranged it.'}]),
    ('larnaca', 'larnaka', 'larnaca', 'Λάρνακα', 'στη Λάρνακα', 'Larnaca', False,
     {'el': 'Αν μένετε ή δουλεύετε στη Λάρνακα, μπορούμε να ξεκινήσουμε με ένα τηλεφώνημα ή μια βιντεοκλήση και να συνεχίσουμε από κοντά, στο γραφείο στη Λευκωσία ή με επίσκεψη κατόπιν συνεννόησης.',
      'en': 'If you live or work in Larnaca, we can start with a phone call or a video call and continue in person, at the office in Nicosia or with a visit by arrangement.'},
     [{'el': 'Ένα πρώτο τηλεφώνημα', 'en': 'A first phone call'}, {'el': 'Μου λέτε με λίγα λόγια τι σας απασχολεί και βρίσκουμε τον τρόπο που σας βολεύει για την πρώτη συνάντηση.', 'en': 'You tell me briefly what is on your mind and we find the way that suits you for the first meeting.'}],
     [{'el': 'Βιντεοκλήση', 'en': 'Video call'}, {'el': 'Η πρώτη συνάντηση με βιντεοκλήση, από όπου βρίσκεστε. Τα χαρτιά σας τα έχετε δίπλα σας.', 'en': 'The first meeting by video call, wherever you are. You keep your papers next to you.'}],
     [{'el': 'Στο γραφείο ή στον χώρο σας', 'en': 'At the office or at your place'}, {'el': 'Στο γραφείο στη Λευκωσία, ή επίσκεψη στη Λάρνακα αφού το κανονίσουμε.', 'en': 'At the office in Nicosia, or a visit in Larnaca once we have arranged it.'}]),
    ('paphos', 'pafos', 'paphos', 'Πάφος', 'στην Πάφο', 'Paphos', False,
     {'el': 'Η Πάφος είναι η πιο μακρινή πόλη από το γραφείο μου, γι’ αυτό εκεί δουλεύουμε κυρίως με βιντεοκλήση και τηλέφωνο. Η εξυπηρέτηση είναι η ίδια: πρώτη συζήτηση, πρόταση με απλά λόγια, και βοήθεια όταν χρειαστεί αποζημίωση.',
      'en': 'Paphos is the furthest city from my office, so there we mostly work by video call and phone. The service is the same: a first conversation, a proposal in plain words, and help when you need to claim.'},
     [{'el': 'Βιντεοκλήση', 'en': 'Video call'}, {'el': 'Ο πιο πρακτικός τρόπος από την Πάφο: περίπου 45 λεπτά, χωρίς ταξίδι, στα Ελληνικά ή στα Αγγλικά.', 'en': 'The most practical way from Paphos: about 45 minutes, no travel, in Greek or English.'}],
     [{'el': 'Τηλέφωνο και WhatsApp', 'en': 'Phone and WhatsApp'}, {'el': 'Για ερωτήσεις, αλλαγές ή μια αποζημίωση, είμαι ένα τηλεφώνημα ή ένα μήνυμα μακριά.', 'en': 'For questions, changes or a claim, I am one phone call or one message away.'}],
     [{'el': 'Από κοντά, όταν χρειάζεται', 'en': 'In person, when needed'}, {'el': 'Μια επίσκεψη στην Πάφο κανονίζεται κατόπιν συνεννόησης, ή συναντιόμαστε στο γραφείο όταν βρίσκεστε στη Λευκωσία.', 'en': 'A visit in Paphos can be arranged, or we meet at the office when you are in Nicosia.'}]),
    ('famagusta', 'ammochostos', 'famagusta', 'Αμμόχωστος', 'στην Αμμόχωστο', 'Famagusta', False,
     {'el': 'Για την ελεύθερη επαρχία Αμμοχώστου, όπως το Παραλίμνι, την Αγία Νάπα και το Δερύνεια, οι συναντήσεις γίνονται με βιντεοκλήση ή τηλεφωνικά, και από κοντά κατόπιν συνεννόησης.',
      'en': 'For the free Famagusta district, such as Paralimni, Ayia Napa and Deryneia, we meet by video call or by phone, and in person by arrangement.'},
     [{'el': 'Βιντεοκλήση ή τηλέφωνο', 'en': 'Video call or phone'}, {'el': 'Όλη η πρώτη συζήτηση γίνεται από απόσταση, την ώρα που σας βολεύει.', 'en': 'The whole first conversation can happen remotely, at a time that suits you.'}],
     [{'el': 'Πρόταση με απλά λόγια', 'en': 'A proposal in plain words'}, {'el': 'Σας εξηγώ την πρόταση στην οθόνη και την έχετε και γραπτώς, για να τη σκεφτείτε με την ησυχία σας.', 'en': 'I explain the proposal on screen and you get it in writing, to think it over in your own time.'}],
     [{'el': 'Από κοντά, κατόπιν συνεννόησης', 'en': 'In person, by arrangement'}, {'el': 'Στο γραφείο στη Λευκωσία, ή επίσκεψη στην περιοχή σας αφού το κανονίσουμε.', 'en': 'At the office in Nicosia, or a visit in your area once we have arranged it.'}]),
]
for _cid, _el, _en, _nel, _, _nen, *_ in CITIES:
    SLUGS['city-' + _cid] = {'el': _el, 'en': _en}
    T['nav']['city-' + _cid] = {'el': _nel, 'en': _nen}

def city_links(lang, current=''):
    el = lang == 'el'
    return ('<nav class="jump city-links" aria-label="' + ('Πόλεις' if el else 'Cities') + '">'
            + ''.join(f'<a href="{url("city-" + c[0], lang)}"' + (' aria-current="page"' if c[0] == current else '') + f'>{c[3] if el else c[5]}</a>' for c in CITIES) + '</nav>')

def make_city_page(cid):
    c = next(x for x in CITIES if x[0] == cid)
    _, _, _, name_el, in_el, name_en, office, lead, *ways = c
    def page(lang):
        el = lang == 'el'
        name = name_el if el else name_en
        title = f'Ασφαλιστικός Σύμβουλος {in_el}: ζωή, υγεία, σύνταξη' if el else f'Insurance Advisor in {name_en}: life, health, retirement'
        desc = (f'Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος. Συναντήσεις {in_el} ' + ('στο γραφείο, με βιντεοκλήση ή τηλεφωνικά.' if office else 'με βιντεοκλήση ή τηλεφωνικά, και από κοντά κατόπιν συνεννόησης.') if el else
                f'Giannis Farazis, Insurance Advisor. Meetings in {name_en} ' + ('at the office, by video call or by phone.' if office else 'by video call or phone, and in person by arrangement.'))
        ld = [{'@context': 'https://schema.org', '@type': 'Service', 'name': title, 'serviceType': 'Life, health and retirement insurance advice',
               'provider': {'@id': BASE + '/#person'}, 'areaServed': {'@type': 'City', 'name': name, 'containedInPlace': {'@type': 'Country', 'name': 'Κύπρος' if el else 'Cyprus'}},
               'availableChannel': [{'@type': 'ServiceChannel', 'serviceLocation': {'@type': 'Place', 'name': 'Office' if not el else 'Γραφείο', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Λεωφόρος Στροβόλου 124Γ, 5ος όροφος' if el else '124C Strovolou Avenue, 5th floor', 'addressLocality': 'Λευκωσία' if el else 'Nicosia', 'addressCountry': 'CY'}}, 'servicePhone': {'@type': 'ContactPoint', 'telephone': TEL}}],
               'url': BASE + url('city-' + cid, lang)}]
        ics = CITY_ICONS[cid]
        cards = ''.join(f'<li><span class="meet-facts__ico">{ICON[ics[i]]}</span><h3>{L(t, lang)}</h3><p>{L(d, lang)}</p></li>' for i, (t, d) in enumerate(ways))
        topics = [x for x in SOLUTIONS if x[0] in ('life', 'health', 'retirement', 'review')]
        addr = OFFICE_EL if el else OFFICE_EN
        maps = 'https://www.google.com/maps/search/?api=1&query=' + 'Strovolou+Avenue+124C+Nicosia+Cyprus'
        return head(lang, 'city-' + cid, title, desc, ld) + page_head(name, L(lead, lang), 'city-' + cid, lang=lang,
            kicker=('Ασφαλιστικός Σύμβουλος ' + in_el) if el else ('Insurance Advisor in ' + name_en), extra=actions(lang)) + f'''
<section class="section section--tight"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{('Πώς συναντιόμαστε ' + in_el) if el else ('How we meet in ' + name_en)}</h2></div>
<ul class="meet-facts">{cards}</ul>
<div class="office-line"><span class="office-line__ico">{ICON['office']}</span><p><b>{'Το γραφείο' if el else 'The office'}</b>{addr}<br><a href="tel:{TEL}">{PHONE}</a> · <a href="tel:{OFFICE_TEL}">{OFFICE}</a> · <a href="{maps}" rel="noopener">{'Οδηγίες στον χάρτη' if el else 'Directions on the map'}</a></p></div>
</div></section>
{film_band(lang, 'fg-cities', 'Από όπου κι αν είστε στην Κύπρο' if el else 'Wherever you are in Cyprus', poster=cid)}
<section class="section tint"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Τι μπορούμε να δούμε μαζί' if el else 'What we can look at together'}</h2>
<p class="lead">{'Τα θέματα που ρωτούν πιο συχνά οι πελάτες, και όλα τα υπόλοιπα στη σελίδα Λύσεις.' if el else 'The subjects clients ask about most often, and everything else on the Solutions page.'}</p></div>
{sol_cards(lang, topics, photos=False, cls=' cards--4')}
<div class="actions"><a class="btn btn-ghost" href="{url('solutions', lang)}">{'Όλες οι λύσεις' if el else 'All solutions'}{ICON['arrow']}</a><a class="btn btn-ghost" href="{url('first', lang)}">{L(T['nav']['first'], lang)}{ICON['arrow']}</a></div>
</div></section>
<section class="section"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Και σε άλλες πόλεις' if el else 'Other cities'}</h2>
<p>{'Η ίδια εξυπηρέτηση σε όλη την Κύπρο, στα Ελληνικά και στα Αγγλικά.' if el else 'The same service across Cyprus, in Greek and English.'}</p></div>
{city_links(lang, cid)}
</div></section>''' + cta_band(lang) + foot(lang)
    return page

CITY_ICONS = {'nicosia': ['office', 'video', 'pin'], 'limassol': ['video', 'phone', 'pin'], 'larnaca': ['phone', 'video', 'office'],
              'paphos': ['video', 'wa', 'pin'], 'famagusta': ['video', 't-review', 'pin']}

def page_employers(lang):
    """Ideas track 12 (14 Oct 2026): «Ενημέρωση για το προσωπικό σας» — a free talk for a company's staff on GESY,
    pensions, provident funds and group LIFE / HEALTH plans. No general insurance. The call-back form (topic business)
    is how an employer asks for it."""
    el = lang == 'el'
    title = 'Ενημέρωση για το προσωπικό σας: ΓεΣΥ, σύνταξη, ταμείο προνοίας' if el else 'A talk for your staff: GESY, pensions, provident funds'
    desc = ('Δωρεάν ενημέρωση για τους εργαζόμενους της επιχείρησής σας: ΓεΣΥ, σύνταξη, ταμεία προνοίας και ομαδικά σχέδια ζωής και υγείας, με απλά λόγια.' if el
            else 'A free talk for your employees: GESY, pensions, provident funds and group life and health plans, in plain words.')
    themes = ([('t-health', 'ΓεΣΥ: τι καλύπτει και τι όχι', 'Προσωπικός γιατρός, ειδικοί, εξετάσεις και νοσηλεία, και πού ένα ιδιωτικό ή ομαδικό σχέδιο υγείας το συμπληρώνει.'),
               ('sun', 'Η σύνταξη των Κοινωνικών Ασφαλίσεων', 'Πώς υπολογίζεται σε γενικές γραμμές, γιατί σπάνια φτάνει, και τι σημαίνει να ξεκινήσει κανείς νωρίς.'),
               ('t-savings', 'Ταμείο προνοίας', 'Πώς λειτουργούν οι εισφορές εργοδότη και εργαζομένου, και τι να κοιτάζει κανείς στην ετήσια κατάσταση.'),
               ('t-group', 'Ομαδικά σχέδια ζωής και υγείας', 'Τι μπορεί να περιλαμβάνει ένα ομαδικό σχέδιο και πώς συνδυάζεται με όσα έχει ήδη κάθε εργαζόμενος.')] if el else
              [('t-health', 'GESY: what it covers and what it does not', 'Personal doctor, specialists, tests and hospital care, and where a private or group health plan complements it.'),
               ('sun', 'The Social Insurance pension', 'How it is worked out in broad terms, why it rarely covers everything, and what starting early means.'),
               ('t-savings', 'Provident funds', 'How employer and employee contributions work, and what to look at in the yearly statement.'),
               ('t-group', 'Group life and health plans', 'What a group plan can include and how it fits with what each employee already has.')])
    how = (['Διάρκεια περίπου 30 έως 45 λεπτά, με χρόνο για ερωτήσεις.', 'Στον χώρο σας, κατόπιν συνεννόησης, ή με βιντεοκλήση για ομάδες σε διαφορετικά σημεία.', 'Στα Ελληνικά ή στα Αγγλικά.', 'Χωρίς κόστος για την επιχείρηση και χωρίς υποχρέωση για κανέναν.', 'Γενική ενημέρωση, όχι πώληση. Όποιος εργαζόμενος θέλει, μιλάμε ξεχωριστά αργότερα.'] if el else
           ['About 30 to 45 minutes, with time for questions.', 'At your premises, by arrangement, or by video call for teams in different places.', 'In Greek or English.', 'No cost to the business and no obligation for anyone.', 'General information, not a sales pitch. Any employee who wants to can talk to me separately later.'])
    ul = lambda xs: '<ul class="ticks">' + ''.join(f'<li>{ICON["check"]}{x}</li>' for x in xs) + '</ul>'
    cards = '<ul class="meet-facts meet-facts--2">' + ''.join(f'<li><span class="meet-facts__ico">{ICON[i]}</span><h3>{t}</h3><p>{d}</p></li>' for i, t, d in themes) + '</ul>'
    note = ('Η ενημέρωση είναι γενική και δεν αποτελεί εξατομικευμένη συμβουλή.' if el
            else 'The talk is general information and is not personal advice.')
    return head(lang, 'employers', title, desc) + page_head(L(T['nav']['employers'], lang),
        'Μια δωρεάν ενημέρωση για τους εργαζόμενους της επιχείρησής σας, με απλά λόγια.' if el else 'A free talk for the people who work for you, in plain words.', 'staff-talks', lang=lang,
        trail=[(L(T['nav']['solutions'], lang), url('solutions', lang, 'group'))],
        extra=f'<div class="actions"><a class="btn btn-primary" href="#call-me">{ICON["phone"]}{"Ζητήστε μια ενημέρωση" if el else "Ask for a talk"}</a></div>') + f'''
<section class="section"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Τι καλύπτει η ενημέρωση' if el else 'What the talk covers'}</h2>
<p class="lead">{'Θέματα που αφορούν κάθε εργαζόμενο, χωρίς ορολογία.' if el else 'Subjects that matter to every employee, without jargon.'}</p></div>
{cards}
</div></section>
{film_band(lang, 'fg-employers', 'Η ενημέρωση, σε ένα σύντομο βίντεο' if el else 'The talk, in a short film')}
<section class="section tint"><div class="wrap callback-wrap">
<div class="callback-side"><hr class="rule"><h2>{'Πώς γίνεται' if el else 'How it works'}</h2>{ul(how)}<p class="note">{note}</p></div>
{callback_form(lang, topic='business', title='Ζητήστε μια ενημέρωση' if el else 'Ask for a talk', lead='Αφήστε όνομα και τηλέφωνο και σας καλώ για να κανονίσουμε μέρα, χώρο και διάρκεια.' if el else 'Leave your name and phone number and I will call you to agree a day, a place and the length.')}
</div></section>''' + cta_band(lang) + callback_script() + foot(lang)

def vcard():
    """the «Save contact» file (vCard 3.0, written at build time): name, role, the two approved phones, website,
    WhatsApp, LinkedIn, office address. No e-mail address (owner's rule); no company name (Eurolife only on Contact)."""
    lines = ['BEGIN:VCARD', 'VERSION:3.0', 'N:Farazis;Giannis;;;', 'FN:Giannis Farazis (Γιάννης Φαραζής)',
             'TITLE:Insurance Advisor / Ασφαλιστικός Σύμβουλος',
             f'TEL;TYPE=CELL,WORK,VOICE:{TEL}', f'TEL;TYPE=WORK,VOICE:{OFFICE_TEL}',
             'ADR;TYPE=WORK:;5th floor;124C Strovolou Avenue;Nicosia;;;Cyprus',
             f'URL:{BASE}/', f'X-SOCIALPROFILE;TYPE=linkedin:{LINKEDIN}', f'URL;TYPE=WhatsApp:{WHATSAPP}',
             f'PHOTO;VALUE=URI:{BASE}/assets/img/giannis-farazis-portrait.jpg', 'NOTE:Life\\, health\\, retirement and savings · Nicosia\\, all of Cyprus',
             'END:VCARD']
    return '\r\n'.join(lines) + '\r\n'

CARD_URL = BASE + '/card/'

def page_card(lang):
    """Ideas track 42 (14 Oct 2026): the digital business card. «Save contact» downloads the vCard; the QR code (made at
    build time by tools/qr.py, no network) always points to https://farazisgiannis.com/card/ and can be printed."""
    el = lang == 'el'
    title = 'Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος: ψηφιακή κάρτα' if el else 'Giannis Farazis, Insurance Advisor: digital business card'
    desc = ('Τηλέφωνα, WhatsApp, LinkedIn και ραντεβού σε μία σελίδα. Αποθηκεύστε την επαφή στο κινητό σας.' if el
            else 'Phones, WhatsApp, LinkedIn and appointments on one page. Save the contact to your phone.')
    rows = [(ICON['phone'], 'Κινητό' if el else 'Mobile', f'<a href="tel:{TEL}">{PHONE}</a>'),
            (ICON['phone'], 'Γραφείο' if el else 'Office', f'<a href="tel:{OFFICE_TEL}">{OFFICE}</a>'),
            (ICON['wa'], 'WhatsApp', f'<a href="{WHATSAPP}" rel="noopener">{PHONE}</a>'),
            (ICON['arrow'], 'LinkedIn', f'<a href="{LINKEDIN}" rel="noopener">Giannis Farazis</a>'),
            (ICON['cy'], 'Γραφείο, διεύθυνση' if el else 'Office address', OFFICE_EL if el else OFFICE_EN)]
    rl = ''.join(f'<li><span class="bcard__ico">{i}</span><span><small>{a}</small>{b}</span></li>' for i, a, b in rows)
    qr_alt = 'Κωδικός QR για τη σελίδα farazisgiannis.com/card' if el else 'QR code for farazisgiannis.com/card'
    return head(lang, 'card', title, desc) + f'''
<section class="section bcard-sec"><div class="wrap">
<article class="bcard on-dark">
<div class="bcard__top">{portrait('Ο Γιάννης Φαραζής' if el else 'Giannis Farazis', eager=True, n='3')}
<div><h1>{L(T['name'], lang)}</h1><p class="bcard__role">{L(T['role'], lang)}</p><p class="bcard__where">{L(T['where'], lang)}</p></div></div>
<ul class="bcard__rows">{rl}</ul>
<div class="bcard__actions">
<a class="btn btn-primary" href="/assets/card/giannis-farazis.vcf" download="giannis-farazis.vcf">{ICON['check']}{'Αποθήκευση επαφής' if el else 'Save contact'}</a>
<a class="btn btn-ghost" href="{url('booking', lang)}">{ICON['cal']}{L(T['nav']['booking'], lang)}</a>
<a class="btn btn-ghost" href="tel:{TEL}">{ICON['phone']}{L(T['call'], lang)}</a>
</div>
</article>
<div class="bcard-qr">
<img src="/assets/card/card-qr.svg" width="290" height="290" alt="{qr_alt}">
<p>{'Σκανάρετε για να ανοίξει αυτή η κάρτα: farazisgiannis.com/card' if el else 'Scan to open this card: farazisgiannis.com/card'}</p>
<p class="no-print"><a href="/assets/card/card-qr.png" download="farazisgiannis-card-qr.png">{'Κατέβασμα QR (PNG)' if el else 'Download the QR code (PNG)'}</a> · <a href="/assets/card/card-qr.svg" download="farazisgiannis-card-qr.svg">SVG</a> · <button class="linkbtn" type="button" data-print>{'Εκτύπωση' if el else 'Print'}</button></p>
</div>
</div></section>''' + foot(lang)

# Client stories (ideas track 5, 14 Oct 2026). EMPTY on purpose: nothing is invented. A story is shown only when it is
# added here with the client's written consent on file. While the list has no such story, the page /istories/ is NOT
# built, not linked and not in the sitemap. Fields (all el/en; ru through i18n/ru.json):
#   {'id': 'family-mortgage', 'consent_on_file': 'yes', 'consent_date': 'YYYY-MM-DD',
#    'title': {'el': …, 'en': …}, 'situation': {…}, 'what_we_did': {…}, 'outcome': {…}}
# Anonymous: no names, no ages that identify, no insurer names, no amounts unless the client agreed in writing.
STORIES = []

def stories_published():
    return [x for x in STORIES if str(x.get('consent_on_file', '')).lower() == 'yes' and x.get('consent_date')]

def page_stories(lang):
    el = lang == 'el'
    title = 'Ιστορίες πελατών' if el else 'Client stories'
    desc = ('Ανώνυμες, αληθινές περιπτώσεις, δημοσιευμένες με τη γραπτή συγκατάθεση των πελατών.' if el
            else 'Anonymous, real cases, published with the clients’ written consent.')
    items = ''.join(f'''<article class="story" id="{esc(x['id'])}"><h2>{esc(L(x['title'], lang))}</h2>
<h3>{'Η κατάσταση' if el else 'The situation'}</h3><p>{esc(L(x['situation'], lang))}</p>
<h3>{'Τι κάναμε' if el else 'What we did'}</h3><p>{esc(L(x['what_we_did'], lang))}</p>
<h3>{'Το αποτέλεσμα' if el else 'The outcome'}</h3><p>{esc(L(x['outcome'], lang))}</p></article>''' for x in stories_published())
    note = ('Κάθε ιστορία δημοσιεύεται ανώνυμα και μόνο με γραπτή συγκατάθεση του πελάτη. Κάθε περίπτωση είναι διαφορετική· οι ιστορίες δεν αποτελούν υπόσχεση αποτελέσματος.' if el
            else 'Every story is published anonymously and only with the client’s written consent. Every case is different; the stories do not promise any result.')
    return head(lang, 'stories', title, desc) + page_head(title, desc, lang=lang) + f'''
<section class="section"><div class="wrap prose stories">{items}<p class="note">{note}</p></div></section>''' + cta_band(lang) + foot(lang)

# Questions and answers (14 Oct 2026 features): only what the rest of the site already says, with schema.org FAQPage.
# No prices, no promises, nothing about other kinds of insurance.
FAQ = [
    ({'el': 'Πόσο διαρκεί η πρώτη συνάντηση και πού γίνεται;', 'en': 'How long is the first meeting, and where is it?'},
     {'el': 'Περίπου 45 λεπτά. Γίνεται στο γραφείο στη Λευκωσία (Λεωφόρος Στροβόλου 124Γ, 5ος όροφος), με βιντεοκλήση ή τηλεφωνικά, όπως σας βολεύει.',
      'en': 'About 45 minutes. It takes place at the office in Nicosia (124C Strovolou Avenue, 5th floor), by video call or by phone, whichever suits you.'}),
    ({'el': 'Δεσμεύομαι σε κάτι αν συναντηθούμε;', 'en': 'Am I committing to anything if we meet?'},
     {'el': 'Όχι. Η πρώτη συνάντηση είναι γνωριμία και καταγραφή αναγκών· δεν υπογράφεται αίτηση ούτε συμβόλαιο. Αν θέλετε να συνεχίσουμε, ετοιμάζω πρόταση με απλά λόγια και αποφασίζετε όταν είστε έτοιμοι.',
      'en': 'No. The first meeting is about getting to know you and noting what you need; no application or policy is signed. If you want to go on, I prepare a proposal in plain words and you decide when you are ready.'}),
    ({'el': 'Μένω εκτός Λευκωσίας. Μπορούμε να συνεργαστούμε;', 'en': 'I live outside Nicosia. Can we still work together?'},
     {'el': 'Ναι. Εξυπηρετώ πελάτες σε όλη την Κύπρο: με βιντεοκλήση ή τηλεφωνικά, και από κοντά κατόπιν συνεννόησης.',
      'en': 'Yes. I work with clients across Cyprus: by video call or by phone, and in person by arrangement.'}),
    ({'el': 'Σε ποιες γλώσσες γίνονται οι συναντήσεις;', 'en': 'Which languages do you work in?'},
     {'el': 'Στα Ελληνικά και στα Αγγλικά.', 'en': 'Greek and English.'}),
    ({'el': 'Με ποια θέματα μπορείτε να με βοηθήσετε;', 'en': 'What can you help me with?'},
     {'el': 'Ασφάλεια ζωής, ιατροφαρμακευτική κάλυψη, προσωπικό ατύχημα, σύνταξη, αποταμίευση και επενδυτικά προγράμματα, σπουδές παιδιών, προστασία δανείου, προστασία επιχείρησης και ομαδικά σχέδια, θέματα ξένων κατοίκων και επανεξέταση των συμβολαίων που ήδη έχετε.',
      'en': 'Life insurance, health and medical cover, personal accident, retirement, savings and investment-linked plans, children’s education, loan protection, business protection and group plans, questions for expats, and a review of the policies you already have.'}),
    ({'el': 'Μπορείτε να δείτε τα συμβόλαια που ήδη έχω;', 'en': 'Can you look at the policies I already have?'},
     {'el': 'Ναι. Τα βλέπουμε μαζί, με απλά λόγια: τι καλύπτουν, πού υπάρχουν κενά ή επικαλύψεις, ποιοι είναι οι δικαιούχοι και αν ταιριάζουν ακόμα στη ζωή σας.',
      'en': 'Yes. We go through them together, in plain words: what they cover, where the gaps or overlaps are, who the beneficiaries are, and whether they still fit your life.'}),
    ({'el': 'Πόσο κοστίζει μια ασφάλεια ζωής;', 'en': 'How much does life insurance cost?'},
     {'el': 'Εξαρτάται από την ηλικία, την υγεία, το ποσό και τα χρόνια της κάλυψης, γι’ αυτό δεν δίνω τιμές χωρίς να γνωρίζω την περίπτωσή σας. Η πρόταση που ετοιμάζω γράφει καθαρά τι καλύπτει, τι δεν καλύπτει και πόσο κοστίζει.',
      'en': 'It depends on age, health, the amount and the number of years of cover, so I do not quote prices without knowing your case. The proposal I prepare states clearly what it covers, what it does not, and what it costs.'}),
    ({'el': 'Εκπίπτουν τα ασφάλιστρα ζωής από τον φόρο;', 'en': 'Are life premiums tax-deductible?'},
     {'el': 'Αν φορολογείστε στην Κύπρο, τα ασφάλιστρα ζωής εκπίπτουν από το φορολογητέο εισόδημα έως το 7% του κεφαλαίου ασφάλισης, μέσα στο συνολικό όριο του ενός πέμπτου του εισοδήματος για τις σχετικές εκπτώσεις. Η έκπτωση εξαρτάται από την προσωπική σας περίπτωση. Πηγή: PwC Worldwide Tax Summaries – Cyprus (Οκτώβριος 2026).',
      'en': 'If you pay tax in Cyprus, life premiums are deductible from taxable income up to 7% of the sum insured, within the overall limit of one fifth of income for the related deductions. The relief depends on your own circumstances. Source: PwC Worldwide Tax Summaries – Cyprus (October 2026).'}),
    ({'el': 'Έχω ΓεΣΥ. Χρειάζομαι και ιδιωτικό σχέδιο υγείας;', 'en': 'I have GESY. Do I also need a private health plan?'},
     {'el': 'Όχι πάντα. Το ΓεΣΥ καλύπτει προσωπικό γιατρό, ειδικούς, εξετάσεις, φάρμακα και νοσηλεία σε παρόχους που συμμετέχουν. Ένα ιδιωτικό σχέδιο το συμπληρώνει όταν θέλετε θεραπεία εκτός ΓεΣΥ, κάλυψη στο εξωτερικό, ιδιωτικό δωμάτιο ή ευελιξία στον χρόνο.',
      'en': 'Not always. GESY covers a personal doctor, specialists, tests, medicines and hospital care with participating providers. A private plan complements it when you want treatment outside GESY, cover abroad, a private room or flexibility over timing.'}),
    ({'el': 'Η ασφάλεια που ζητά η τράπεζα για το στεγαστικό προστατεύει την οικογένειά μου;', 'en': 'Does the cover the bank asks for with my mortgage protect my family?'},
     {'el': 'Εξοφλεί το δάνειο, όχι όμως το εισόδημα της οικογένειας. Αξίζει να δούμε αν η κάλυψη ταιριάζει με το υπόλοιπο και τη διάρκεια του δανείου, και αν η οικογένεια χρειάζεται κάτι επιπλέον.',
      'en': 'It pays off the loan; it does not replace your family’s income. It is worth checking that the cover matches the balance and term of the loan, and whether your family needs something more.'}),
    ({'el': 'Τι κάνω όταν χρειαστεί αποζημίωση;', 'en': 'What do I do when I need to claim?'},
     {'el': 'Ενημερώστε την ασφαλιστική εταιρεία όσο πιο νωρίς γίνεται, γιατί πολλά συμβόλαια έχουν προθεσμίες, και κρατήστε αντίγραφα από ό,τι δίνετε. Αν είστε πελάτης μου, καλέστε με πριν στείλετε τα έγγραφα και τα βλέπουμε μαζί. Η λίστα «Έγγραφα για αποζημίωση» στη σελίδα Οδηγοί δείχνει τι ζητείται συνήθως.',
      'en': 'Tell the insurer as early as you can, because many policies have deadlines, and keep copies of everything you hand in. If you are my client, call me before you send the documents and we will go through them together. The “Documents for a claim” checklist on the Guides page shows what is usually asked for.'}),
    ({'el': 'Τι γίνεται με τα στοιχεία που γράφω στις φόρμες;', 'en': 'What happens to the details I enter in the forms?'},
     {'el': 'Χρησιμοποιούνται μόνο για να απαντήσω στο αίτημά σας. Ο ιστότοπος δεν χρησιμοποιεί cookies ούτε εργαλεία παρακολούθησης. Μη γράφετε ιατρικά στοιχεία ή αριθμούς λογαριασμών στις φόρμες. Όλες οι λεπτομέρειες βρίσκονται στην πολιτική απορρήτου.',
      'en': 'They are used only to reply to your request. This website uses no cookies and no tracking tools. Please do not write medical details or account numbers in the forms. All the details are in the privacy policy.'}),
]

def page_faq(lang):
    el = lang == 'el'
    title = 'Συχνές ερωτήσεις: πρώτη συνάντηση, κόστος, αποζημιώσεις' if el else 'Questions and answers: first meeting, costs, claims'
    desc = ('Σύντομες απαντήσεις: πόσο διαρκεί η πρώτη συνάντηση, αν δεσμεύεστε, γλώσσες, φορολογική έκπτωση, ΓεΣΥ, στεγαστικό, αποζημιώσεις και στοιχεία.' if el
            else 'Short answers: how long the first meeting takes, whether you commit to anything, languages, tax relief, GESY, mortgages, claims and your details.')
    ld = [{'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': L(q, lang), 'acceptedAnswer': {'@type': 'Answer', 'text': L(a, lang)}} for q, a in FAQ]}]
    items = ''.join(f'<details class="qa"{" open" if i == 0 else ""}><summary><h2>{L(q, lang)}</h2><span class="qa__sign" aria-hidden="true"></span></summary><div class="qa__a"><p>{L(a, lang)}</p></div></details>'
                    for i, (q, a) in enumerate(FAQ))
    more = link_cards(lang, [('list', L(T['nav']['first'], lang), 'Τι συζητάμε, τι να φέρετε και τι δεν χρειάζεται.' if el else 'What we talk about, what to bring and what you do not need.', url('first', lang)),
                             ('t-review', L(T['nav']['events'], lang), 'Τι να ελέγξετε σε κάθε μεγάλη αλλαγή της ζωής.' if el else 'What to check at each big change in life.', url('events', lang)),
                             ('cal', L(T['nav']['booking'], lang), 'Διαλέξτε μέρα και ώρα από τις ελεύθερες ώρες.' if el else 'Choose a day and time from the free times.', url('booking', lang))])
    return head(lang, 'faq', title, desc, ld) + page_head(L(T['nav']['faq'], lang),
        'Σύντομες απαντήσεις στις ερωτήσεις που ακούω πιο συχνά πριν από μια πρώτη συνάντηση.' if el else 'Short answers to the questions I hear most often before a first meeting.', lang=lang, extra=print_button(lang)) + f'''
<section class="section section--tight"><div class="wrap faq-grid">
<div class="faq">{items}</div>
<aside class="faq-aside no-print"><h2 class="aside-title">{'Δεν βρήκατε την απάντηση;' if el else 'Did not find the answer?'}</h2>
<p>{'Ρωτήστε με απευθείας: τηλεφωνικά, στο WhatsApp ή με ένα αίτημα κλήσης.' if el else 'Ask me directly: by phone, on WhatsApp or with a call-back request.'}</p>
{actions(lang, book=False)}</aside>
</div></section>
<section class="section tint no-print"><div class="wrap"><div class="section-head"><hr class="rule"><h2>{'Επόμενο βήμα' if el else 'Next step'}</h2></div>{more}</div></section>''' + cta_band(lang) + foot(lang)

# «Αλλαγές στη ζωή σας» (14 Oct 2026 features): what to check, and which papers to have ready, at each big change in
# life — life, health, accident, pension and savings cover only. General information drawn from the rest of the site
# (Solutions, Guides, the checklists); each event can be printed on its own (site.js, data-print-one).
# (id, icon, title, when, [check], [papers], (checklist stem or None))
EVENTS = [
    ('marriage', 'ring', {'el': 'Γάμος ή συμβίωση', 'en': 'Marriage or moving in together'},
     {'el': 'Όταν δύο ζωές και δύο εισοδήματα γίνονται ένα νοικοκυριό.', 'en': 'When two lives and two incomes become one household.'},
     [{'el': 'Οι δικαιούχοι στα συμβόλαια ζωής είναι αυτοί που θέλετε σήμερα;', 'en': 'Are the beneficiaries on your life policies the people you want today?'},
      {'el': 'Αν το ένα εισόδημα έλειπε, θα έφτανε το άλλο για τα έξοδα του σπιτιού;', 'en': 'If one income were missing, would the other cover the household’s costs?'},
      {'el': 'Υπάρχουν καλύψεις υγείας που επικαλύπτονται ή κενά που δεν καλύπτει κανένα συμβόλαιο;', 'en': 'Is any health cover duplicated, or is there a gap no policy covers?'}],
     [{'el': 'Τα συμβόλαια που έχει ο καθένας: ζωής, υγείας, ατυχήματος, αποταμίευσης', 'en': 'The policies each of you has: life, health, accident, savings'},
      {'el': 'Ενημέρωση από ταμείο προνοίας ή ομαδικό σχέδιο της δουλειάς, αν υπάρχει', 'en': 'Any statement from a provident fund or a group plan at work'}], 'etisios-elegxos'),
    ('baby', 'baby', {'el': 'Ένα παιδί έρχεται', 'en': 'A child on the way'},
     {'el': 'Η πιο μεγάλη αλλαγή στο πόσα χρόνια χρειάζεται προστασία η οικογένεια.', 'en': 'The biggest change in how many years your family needs protecting.'},
     [{'el': 'Φτάνει το ποσό της ασφάλειας ζωής για τα χρόνια μέχρι να ανεξαρτητοποιηθεί το παιδί;', 'en': 'Is your life cover enough for the years until the child is independent?'},
      {'el': 'Μπορεί το παιδί να προστεθεί στο σχέδιο υγείας σας, και από πότε;', 'en': 'Can the child be added to your health plan, and from when?'},
      {'el': 'Θέλετε να ξεκινήσει από νωρίς ένα σχέδιο για τις σπουδές του;', 'en': 'Would you like a plan for the child’s studies to start early?'},
      {'el': 'Οι δικαιούχοι χρειάζονται αλλαγή;', 'en': 'Do the beneficiaries need changing?'}],
     [{'el': 'Τα συμβόλαια ζωής και υγείας που ήδη έχετε', 'en': 'The life and health policies you already have'},
      {'el': 'Ένα κατά προσέγγιση μηνιαίο εισόδημα και τα βασικά έξοδα του νοικοκυριού', 'en': 'A rough monthly household income and the main costs'}], None),
    ('home', 't-loan', {'el': 'Σπίτι με στεγαστικό δάνειο', 'en': 'A home with a mortgage'},
     {'el': 'Η τράπεζα ζητά συνήθως ασφάλεια ζωής για το ποσό και τη διάρκεια του δανείου.', 'en': 'The bank usually asks for life cover for the amount and term of the loan.'},
     [{'el': 'Η κάλυψη ταιριάζει με το υπόλοιπο και τη διάρκεια του δανείου;', 'en': 'Does the cover match the balance and term of the loan?'},
      {'el': 'Με δύο δανειολήπτες: πρέπει να ασφαλιστούν και οι δύο, και για ποιο ποσό;', 'en': 'With two borrowers: must both be insured, and for what amount?'},
      {'el': 'Η ασφάλεια της τράπεζας εξοφλεί το δάνειο· χρειάζεται η οικογένεια κάτι επιπλέον για το εισόδημα;', 'en': 'The bank’s cover pays off the loan; does your family need something more for its income?'},
      {'el': 'Ανάλογα με την ηλικία και το ποσό μπορεί να ζητηθούν ερωτήσεις ή εξετάσεις υγείας: υπολογίστε τον χρόνο', 'en': 'Depending on age and amount, health questions or tests may be needed: allow time for them'}],
     [{'el': 'Την πρόταση δανείου της τράπεζας: ποσό, διάρκεια, δόση', 'en': 'The bank’s loan offer: amount, term, instalment'},
      {'el': 'Τις ασφάλειες ζωής που ήδη έχετε', 'en': 'The life policies you already have'}], 'stegastiko'),
    ('job', 'work', {'el': 'Νέα δουλειά ή αυτοαπασχόληση', 'en': 'A new job, or working for yourself'},
     {'el': 'Μαζί με τη δουλειά αλλάζουν συχνά και οι καλύψεις που είχατε μέσω εργοδότη.', 'en': 'With the job, the cover you had through an employer often changes too.'},
     [{'el': 'Τι καλύψεις είχατε μέσω της προηγούμενης δουλειάς, και τι έχετε στη νέα;', 'en': 'What cover did you have through your previous job, and what does the new one offer?'},
      {'el': 'Τι γίνεται με το ταμείο προνοίας όταν αλλάζετε εργοδότη;', 'en': 'What happens to your provident fund when you change employer?'},
      {'el': 'Αν γίνεστε αυτοαπασχολούμενος: πώς θα πληρώνατε τα έξοδα αν σταματούσατε να εργάζεστε για μερικούς μήνες;', 'en': 'If you become self-employed: how would you pay your bills if you stopped working for a few months?'},
      {'el': 'Ξεκινάτε ή συνεχίζετε την αποταμίευση για τη σύνταξη;', 'en': 'Are you starting, or carrying on, saving for retirement?'}],
     [{'el': 'Την ετήσια κατάσταση του ταμείου προνοίας', 'en': 'The yearly provident fund statement'},
      {'el': 'Τις πληροφορίες για το ομαδικό σχέδιο της νέας δουλειάς, αν υπάρχει', 'en': 'The details of the new job’s group plan, if there is one'}], None),
    ('moving', 't-expats', {'el': 'Μετακόμιση στην Κύπρο', 'en': 'Moving to Cyprus'},
     {'el': 'Το σύστημα μπορεί να διαφέρει πολύ από αυτό που ξέρετε.', 'en': 'The system may be quite different from what you know.'},
     [{'el': 'Δικαιούστε ΓεΣΥ στη δική σας περίπτωση;', 'en': 'Are you entitled to GESY in your case?'},
      {'el': 'Τι ιδιωτική ασφάλεια υγείας ζητά η άδεια διαμονής σας;', 'en': 'What private health cover does your residence permit ask for?'},
      {'el': 'Αν αγοράζετε σπίτι με δάνειο: τι ασφάλεια ζωής ζητά η τράπεζα, και δέχεται συμβόλαιο που ήδη έχετε;', 'en': 'If you buy a home with a loan: what life cover does the bank ask for, and will it accept a policy you already have?'},
      {'el': 'Πώς θα συμπληρωθεί η σύνταξή σας από τα χρόνια εργασίας εδώ;', 'en': 'How will your pension be topped up for the years you work here?'}],
     [{'el': 'Την τρέχουσα λίστα εγγράφων για την άδεια διαμονής σας', 'en': 'The current list of documents for your residence permit'},
      {'el': 'Τα συμβόλαια που έχετε από τη χώρα σας', 'en': 'The policies you have from your home country'}], None),
    ('studies', 'cap', {'el': 'Τα παιδιά φεύγουν για σπουδές', 'en': 'Your children leave to study'},
     {'el': 'Η στιγμή για την οποία αποταμιεύατε, και μερικά νέα ερωτήματα.', 'en': 'The moment you were saving for, and a few new questions.'},
     [{'el': 'Πότε και πώς πληρώνει το σχέδιο σπουδών: εφάπαξ ή σε δόσεις;', 'en': 'When and how does the education plan pay out: in one sum or in instalments?'},
      {'el': 'Καλύπτει το σχέδιο υγείας το παιδί όσο σπουδάζει στο εξωτερικό;', 'en': 'Does your health plan cover the child while studying abroad?'},
      {'el': 'Χρειάζονται αλλαγή οι δικαιούχοι ή τα ποσά;', 'en': 'Do the beneficiaries or the amounts need changing?'}],
     [{'el': 'Τα έγγραφα του σχεδίου σπουδών και του σχεδίου υγείας', 'en': 'The papers of the education plan and of the health plan'}], None),
    ('retirement', 'sun', {'el': 'Πλησιάζει η σύνταξη', 'en': 'Retirement is getting close'},
     {'el': 'Τα χρόνια που αποταμιεύατε γίνονται εισόδημα.', 'en': 'The years of saving turn into income.'},
     [{'el': 'Πότε λήγουν τα συνταξιοδοτικά και αποταμιευτικά σας σχέδια, και τι επιλογές έχετε: κεφάλαιο ή τακτικό εισόδημα;', 'en': 'When do your pension and savings plans mature, and what are your choices: a lump sum or regular income?'},
      {'el': 'Τι γίνεται με το ομαδικό σχέδιο υγείας της δουλειάς όταν συνταξιοδοτηθείτε;', 'en': 'What happens to your group health plan at work when you retire?'},
      {'el': 'Πόσο εισόδημα θέλετε στη σύνταξη και πόσο λείπει;', 'en': 'How much income do you want in retirement, and how much is missing?'}],
     [{'el': 'Την ετήσια κατάσταση του ταμείου προνοίας', 'en': 'The yearly provident fund statement'},
      {'el': 'Την ενημέρωση από τις Κοινωνικές Ασφαλίσεις για τη σύνταξή σας', 'en': 'Your statement from Social Insurance about your pension'},
      {'el': 'Τα έγγραφα των συνταξιοδοτικών και αποταμιευτικών σχεδίων', 'en': 'The papers of your pension and savings plans'}], None),
    ('separation', 't-review', {'el': 'Διαζύγιο ή χωρισμός', 'en': 'Divorce or separation'},
     {'el': 'Μια δύσκολη στιγμή, που αλλάζει όμως και το ποιος προστατεύεται.', 'en': 'A hard time, which also changes who is protected.'},
     [{'el': 'Οι δικαιούχοι στα συμβόλαια ζωής είναι αυτοί που θέλετε σήμερα;', 'en': 'Are the beneficiaries on your life policies the people you want today?'},
      {'el': 'Ποιος πληρώνει ποιο συμβόλαιο από εδώ και πέρα;', 'en': 'Who pays which policy from now on?'},
      {'el': 'Φτάνει η κάλυψη για τα παιδιά και για τα χρόνια που τη χρειάζονται;', 'en': 'Is the cover enough for the children, and for the years they need it?'}],
     [{'el': 'Όλα τα συμβόλαια που αφορούν εσάς και τα παιδιά', 'en': 'Every policy that concerns you and the children'}], 'etisios-elegxos'),
    ('loss', 'loss', {'el': 'Απώλεια αγαπημένου προσώπου', 'en': 'Losing someone close'},
     {'el': 'Όταν χρειάζεται μια αποζημίωση, ένα βήμα τη φορά.', 'en': 'When a claim is needed, one step at a time.'},
     [{'el': 'Ενημερώστε την ασφαλιστική εταιρεία όσο πιο νωρίς γίνεται: πολλά συμβόλαια έχουν προθεσμίες', 'en': 'Tell the insurer as early as you can: many policies have deadlines'},
      {'el': 'Κρατήστε αντίγραφα από ό,τι δίνετε', 'en': 'Keep copies of everything you hand in'},
      {'el': 'Αν ήταν πελάτης μου, καλέστε με πριν στείλετε τα έγγραφα και τα βλέπουμε μαζί', 'en': 'If they were my client, call me before you send the documents and we will go through them together'}],
     [{'el': 'Τον αριθμό του συμβολαίου', 'en': 'The policy number'},
      {'el': 'Πιστοποιητικό θανάτου και ιατρική βεβαίωση για την αιτία θανάτου', 'en': 'The death certificate and a medical certificate of the cause of death'},
      {'el': 'Τις ταυτότητες των δικαιούχων', 'en': 'The beneficiaries’ ID documents'},
      {'el': 'Αν δεν έχουν οριστεί δικαιούχοι, τα έγγραφα κληρονομιάς ή διαχείρισης που θα ζητηθούν', 'en': 'If no beneficiaries were named, the inheritance or estate papers that will be asked for'}], 'eggrafa-apozimiosis'),
]

def page_events(lang):
    el = lang == 'el'
    pl = 'ru' if RENDER['ru'] else lang
    title = 'Αλλαγές στη ζωή σας: τι να ελέγξετε στις ασφάλειές σας' if el else 'Changes in your life: what to check in your cover'
    desc = ('Γάμος, παιδί, σπίτι με δάνειο, νέα δουλειά, μετακόμιση στην Κύπρο, σπουδές, σύνταξη, απώλεια: τι να ελέγξετε και ποια χαρτιά να έχετε έτοιμα.' if el
            else 'Marriage, a child, a mortgage, a new job, moving to Cyprus, studies, retirement, a loss: what to check and which papers to have ready.')
    jump = '<nav class="jump" aria-label="' + ('Οι αλλαγές' if el else 'The changes') + '">' + ''.join(f'<a href="#{eid}">{L(t, lang)}</a>' for eid, _, t, *_ in EVENTS) + '</nav>'
    pdf_title = {c[1]: c[2] for c in CHECKLISTS}
    body = ''
    for eid, ico, t, when, check, papers, stem in EVENTS:
        pdf = (f'<p class="event__pdf no-print"><a href="/assets/pdf/{pdf_name(stem, pl)}" download>{ICON["clear"]}{esc(pdf_title[stem]["en" if lang == "en" else "el"])} (PDF)</a></p>' if stem else '')
        body += f'''<article class="event" id="{eid}" data-print-one-target>
<header class="event__head"><span class="event__ico">{ICON[ico]}</span><div><h2>{L(t, lang)}</h2><p>{L(when, lang)}</p></div>
<button class="btn btn-ghost btn-sm no-print" type="button" data-print-one="{eid}">{ICON['print']}{'Εκτύπωση' if el else 'Print'}</button></header>
<div class="event__cols"><div><h3>{'Τι να ελέγξετε' if el else 'What to check'}</h3><ul class="ticks">{''.join(f'<li>{ICON["check"]}{L(x, lang)}</li>' for x in check)}</ul></div>
<div><h3>{'Τι να έχετε έτοιμο' if el else 'What to have ready'}</h3><ul class="ticks ticks--doc">{''.join(f'<li>{ICON["clear"]}{L(x, lang)}</li>' for x in papers)}</ul>{pdf}</div></div>
</article>'''
    note = ('Γενική ενημέρωση, όχι εξατομικευμένη συμβουλή. Κάθε ασφαλιστική εταιρεία και κάθε τράπεζα έχει τους δικούς της όρους και μπορεί να ζητήσει κάτι επιπλέον.' if el
            else 'General information, not personal advice. Every insurer and every bank has its own terms and may ask for something more.')
    return head(lang, 'events', title, desc) + page_head(L(T['nav']['events'], lang),
        'Οι μεγάλες στιγμές της ζωής αλλάζουν και το τι χρειάζεστε. Για καθεμία: τι να ελέγξετε και ποια χαρτιά να έχετε έτοιμα.' if el else 'The big moments in life change what you need too. For each one: what to check, and which papers to have ready.',
        lang=lang, trail=[(L(T['nav']['guides'], lang), url('guides', lang))], extra=print_button(lang)) + f'''
<section class="section section--tight"><div class="wrap">{jump}<div class="events">{body}</div><p class="note">{note}</p></div></section>
<section class="section tint no-print"><div class="wrap callback-wrap">
<div class="callback-side"><hr class="rule"><h2>{'Άλλαξε κάτι στη ζωή σας;' if el else 'Has something changed in your life?'}</h2>
<p>{'Φέρτε τα συμβόλαια που έχετε και τα βλέπουμε μαζί, χωρίς δέσμευση. Ή αφήστε μου όνομα και τηλέφωνο και σας καλώ εγώ.' if el else 'Bring the policies you have and we will look at them together, with no commitment. Or leave your name and number and I will call you.'}</p>
<p><a class="btn btn-primary" href="{url('booking', lang)}?topic=review">{ICON['cal']}{L(T['nav']['booking'], lang)}</a></p></div>
{callback_form(lang, topic='review', heading=False)}
</div></section>''' + callback_script() + foot(lang)

def page_privacy(lang):
    el = lang == 'el'
    title = 'Πολιτική απορρήτου' if el else 'Privacy policy'
    desc = 'Ποια στοιχεία συλλέγουν οι φόρμες του ιστότοπου, γιατί, για πόσο, και τα δικαιώματά σας. Χωρίς cookies και χωρίς εργαλεία παρακολούθησης.' if el else 'What the forms on this website collect, why, for how long, and your rights. No cookies and no tracking tools.'
    body = '''<p>Υπεύθυνος επεξεργασίας είναι ο Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος, Λευκωσία (τηλ. +357 97 840941).</p>
<h2>Τι συλλέγουμε και γιατί</h2>
<p>Μόνο ό,τι γράφετε στις φόρμες. Στη φόρμα επικοινωνίας: ονοματεπώνυμο, τηλέφωνο ή e-mail, θέμα και μήνυμα. Τα χρησιμοποιούμε μόνο για να απαντήσουμε στο αίτημά σας. Νομική βάση είναι η συγκατάθεσή σας και τα βήματα που ζητάτε πριν από μια πιθανή σύμβαση.</p>
<h2>Πώς ταξιδεύουν τα στοιχεία</h2>
<p>Η φόρμα στέλνει το μήνυμα μέσω διακομιστή μας στην Ευρωπαϊκή Ένωση (Hetzner, Φινλανδία), ο οποίος το προωθεί με e-mail στο επαγγελματικό γραμματοκιβώτιο του συμβούλου και δεν το αποθηκεύει. Ο ιστότοπος φιλοξενείται στο GitHub Pages (GitHub Inc.), που μπορεί να καταγράφει τεχνικά στοιχεία όπως τη διεύθυνση IP για λόγους ασφάλειας.</p>
<h2>Online ραντεβού</h2>
<p>Η σελίδα «Κλείστε ραντεβού» χρησιμοποιεί το σύστημα ραντεβού του avrastro.com (AVRASTRO). Όσα γράφετε εκεί (όνομα, e-mail, τηλέφωνο, θέμα, τρόπος συνάντησης, σημείωση) αποθηκεύονται σε εκείνο το σύστημα, σας στέλνονται τα e-mail επιβεβαίωσης και υπενθύμισης, και το αίτημα καταχωρίζεται στο σύστημα διαχείρισης πελατών μου. Ισχύει η <a href="https://avrastro.com/privacy/" rel="noopener">πολιτική απορρήτου του avrastro.com</a>. Στοιχεία ραντεβού ανωνυμοποιούνται 24 μήνες μετά την ημερομηνία του ραντεβού.</p>
<p>Αν απαντήσετε στον προαιρετικό «σύντομο έλεγχο αναγκών» της φόρμας ραντεβού (νοικοκυριό, δουλειά, δάνειο, τι έχετε ήδη, τι σας απασχολεί), οι απαντήσεις προστίθενται στη σημείωση του αιτήματος και ισχύουν τα ίδια. Δεν περιλαμβάνει ερωτήσεις υγείας. Τίποτα δεν αποθηκεύεται στον browser σας.</p>
<h2 id="callback">Αίτημα κλήσης («Πάρτε με τηλέφωνο»)</h2>
<p>Η φόρμα «Πάρτε με τηλέφωνο» στέλνει όνομα, τηλέφωνο, το διάστημα της ημέρας που σας βολεύει και το θέμα στο σύστημα του avrastro.com (AVRASTRO), μαζί με τη διεύθυνση της σελίδας από την οποία στάλθηκε. Εκεί αποθηκεύονται, μου στέλνεται ειδοποίηση με e-mail και το αίτημα καταχωρίζεται στο σύστημα διαχείρισης πελατών μου ως κλήση που πρέπει να κάνω. Δεν ζητείται e-mail. Τα χρησιμοποιώ μόνο για να σας καλέσω για αυτό το αίτημα· νομική βάση είναι η συγκατάθεσή σας. Τα στοιχεία του αιτήματος ανωνυμοποιούνται 24 μήνες μετά. Ισχύει και η <a href="https://avrastro.com/privacy/" rel="noopener">πολιτική απορρήτου του avrastro.com</a>.</p>
<h2>Για πόσο τα κρατάμε</h2>
<p>Όσο χρειάζεται για να απαντήσουμε και να εξυπηρετήσουμε το αίτημά σας. Αν δεν προχωρήσει συνεργασία, το μήνυμα διαγράφεται μέσα σε 12 μήνες.</p>
<h2>Cookies και στατιστικά</h2>
<p>Ο ιστότοπος δεν χρησιμοποιεί cookies, Google Analytics ή άλλα εργαλεία παρακολούθησης, και δεν φορτώνει γραμματοσειρές ή σενάρια από τρίτους.</p>
<h2>Τα δικαιώματά σας</h2>
<p>Μπορείτε να ζητήσετε πρόσβαση, διόρθωση ή διαγραφή των στοιχείων σας, να ανακαλέσετε τη συγκατάθεσή σας ή να αντιταχθείτε στην επεξεργασία, καλώντας στο +357 97 840941. Μπορείτε επίσης να υποβάλετε καταγγελία στον Επίτροπο Προστασίας Δεδομένων Προσωπικού Χαρακτήρα (<a href="https://www.dataprotection.gov.cy/" rel="noopener">www.dataprotection.gov.cy</a>).</p>''' if el else '''<p>The controller is Giannis Farazis, Insurance Advisor, Nicosia (tel. +357 97 840941).</p>
<h2>What we collect and why</h2>
<p>Only what you write in the forms. In the contact form: your name, phone or e-mail, topic and message. We use it only to reply to your request. The legal basis is your consent and the steps you ask for before a possible contract.</p>
<h2>How your details travel</h2>
<p>The form sends your message through our server in the European Union (Hetzner, Finland), which forwards it by e-mail to the advisor’s business mailbox and does not store it. The website is hosted on GitHub Pages (GitHub Inc.), which may log technical data such as IP addresses for security.</p>
<h2>Online appointments</h2>
<p>The “Book an appointment” page uses the avrastro.com (AVRASTRO) booking system. What you enter there (name, e-mail, phone, topic, how to meet, note) is stored in that system, used for the confirmation and reminder e-mails, and recorded in my client management system. The <a href="https://avrastro.com/en/privacy/" rel="noopener">avrastro.com privacy notice</a> applies. Appointment details are anonymised 24 months after the appointment date.</p>
<p>If you answer the optional “short needs check” in the booking form (household, work, loans, what you already have, what matters to you), your answers are added to the note of the request and the same applies. It has no health questions. Nothing is stored in your browser.</p>
<h2 id="callback">Call-back requests (“Ask me to call you”)</h2>
<p>The “Ask me to call you” form sends your name, phone number, the part of the day that suits you and the topic to the avrastro.com (AVRASTRO) system, together with the address of the page it was sent from. They are stored there, I am notified by e-mail, and the request is recorded in my client management system as a call I need to make. No e-mail address is asked for. I use these details only to call you about this request; the legal basis is your consent. The request details are anonymised after 24 months. The <a href="https://avrastro.com/en/privacy/" rel="noopener">avrastro.com privacy notice</a> also applies.</p>
<h2>How long we keep it</h2>
<p>As long as needed to reply and deal with your request. If no business follows, the message is deleted within 12 months.</p>
<h2>Cookies and statistics</h2>
<p>This website uses no cookies, no Google Analytics and no other tracking tools, and loads no fonts or scripts from third parties.</p>
<h2>Your rights</h2>
<p>You can ask for access to, correction or erasure of your details, withdraw your consent or object to processing by calling +357 97 840941. You can also complain to the Cyprus Commissioner for Personal Data Protection (<a href="https://www.dataprotection.gov.cy/" rel="noopener">www.dataprotection.gov.cy</a>).</p>'''
    upd = f'<p class="note">{"Τελευταία ενημέρωση" if el else "Last updated"}: {UPDATED}</p>'
    return head(lang, 'privacy', title, desc) + page_head(title, desc, lang=lang) + f'<section class="section"><div class="wrap prose">{body}{upd}</div></section>' + foot(lang)

def redirect_page(to):
    return f'<!doctype html><html lang="el"><head><meta charset="utf-8"><title>Giannis Farazis</title><link rel="canonical" href="{BASE}{to}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={to}"></head><body><p><a href="{to}">farazisgiannis.com{to}</a></p></body></html>\n'

def page_404():
    return (head('el', 'home', 'Η σελίδα δεν βρέθηκε | Giannis Farazis', 'Η σελίδα δεν βρέθηκε.').replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')
            + page_head('Η σελίδα δεν βρέθηκε', 'Page not found') + f'<section class="section"><div class="wrap"><p><a href="/">Αρχική</a> · <a href="/en/">Home</a></p>{actions("el")}</div></section>' + foot('el'))

PAGES = {'home': page_home, 'about': page_about, 'solutions': page_solutions, 'how': page_how, 'guides': page_guides, 'contact': page_contact, 'booking': page_booking, 'first': page_first, 'events': page_events, 'faq': page_faq, 'employers': page_employers, 'card': page_card, 'privacy': page_privacy,
         **{'city-' + c[0]: make_city_page(c[0]) for c in CITIES}}
if stories_published(): PAGES['stories'] = page_stories   # ideas track 5: only with real, consented stories
# addresses of the earlier Design.com site, kept working
LEGACY = {'home': '/', 'contact-us': '/epikoinonia/', 'programs': '/lyseis/', 'about': '/sxetika/', 'vero': '/'}

# preview on https://veroltd.github.io/farazisgiannis-site/ before the domain points here: SITE_PREFIX=/farazisgiannis-site
PREFIX = os.environ.get('SITE_PREFIX', '').rstrip('/')

def write(rel, text):
    if PREFIX and rel.endswith('.html'):
        for a in ('href="/', 'src="/', 'srcset="/', 'poster="/', 'url=/'):
            text = text.replace(a, a[:-1] + PREFIX + '/')
        text = text.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex">', 1)
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f: f.write(text)

import re as _re
RU_RULES = [(_re.compile(r'^© (\d{4}) Giannis Farazis'), r'© \1 Яннис Фаразис'), (_re.compile(r'^PDF · A4 · (\d+) KB$'), r'PDF · A4 · \1 КБ'), (_re.compile(r'^Last updated: (.+)$'), r'Последнее обновление: \1')]
RU_MISSING = set()

def _ru(text):
    """one segment → Russian (whitespace kept); unknown English is left as it is and reported"""
    core = _re.sub(r'\s+', ' ', text).strip()
    if not core or not _re.search(r'[A-Za-z]', core) or _re.search(r'[А-Яа-яЁё]', core) or _re.match(r'^(https?://|#|/|[\w.+-]+@)', core) or core.startswith('width=') or core in LANG_NAME.values() or ' ' not in core and not core[0].isupper(): return text
    if core in RU: out = RU[core]
    else:
        out = None
        for rx, rep in RU_RULES:
            if rx.search(core):
                out = rx.sub(rep, core)
                # the registration placeholder after the copyright
                for k, v in RU.items():
                    if k.startswith('[') and k in out: out = out.replace(k, v)
                break
        if out is None:
            RU_MISSING.add(core); return text
    lead = text[:len(text) - len(text.lstrip())]; trail = text[len(text.rstrip()):]
    return lead + out + trail

def _ru_json(j):
    if isinstance(j, dict): return {k: (_ru(v) if isinstance(v, str) and k in ('name', 'text', 'description', 'jobTitle') else _ru_json(v)) for k, v in j.items()}
    if isinstance(j, list): return [_ru_json(v) for v in j]
    return j

def ru_page(doc):
    """an English page, rendered with RENDER['ru'] on, turned into the Russian edition"""
    parts = _re.split(r'(<script\b[^>]*>.*?</script>)', doc, flags=_re.S)
    out = []
    for part in parts:
        if part.startswith('<script'):
            m = _re.match(r'(<script type="application/ld\+json">)(.*)(</script>)$', part, _re.S)
            if m:
                try: part = m.group(1) + json.dumps(_ru_json(json.loads(m.group(2))), ensure_ascii=False).replace('</', '<\\/') + m.group(3)
                except Exception: pass
            out.append(part); continue
        part = _re.sub(r'(\s(?:alt|aria-label|title|placeholder|data-pause|data-play|content)=")([^"]*)(")', lambda m: m.group(1) + html.escape(_ru(html.unescape(m.group(2))), quote=True) + m.group(3), part)
        part = _re.sub(r'>([^<]+)<', lambda m: '>' + html.escape(_ru(html.unescape(m.group(1))), quote=False) + '<', part)
        out.append(part)
    doc = ''.join(out)
    # links inside the site go to the Russian pages; the language switch and hreflang links keep their own targets
    doc = _re.sub(r'href="/en/', 'href="/ru/', doc)
    doc = doc.replace('href="/ru/" hreflang="en"', 'href="/en/" hreflang="en"')
    doc = _re.sub(r'(<a class="lang" href=")/ru/([^"]*)(" hreflang="en")', r'\1/en/\2\3', doc)
    doc = doc.replace('data-lang="en"', 'data-lang="ru"')
    return doc

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    # digital business card (ideas track 42): the vCard and the QR code of https://farazisgiannis.com/card/, made here
    import sys; sys.path.insert(0, os.path.join(ROOT, 'tools')); import qr
    card = os.path.join(OUT, 'assets', 'card'); os.makedirs(card, exist_ok=True)
    with open(os.path.join(card, 'giannis-farazis.vcf'), 'w', encoding='utf-8', newline='') as f: f.write(vcard())
    m = qr.encode(CARD_URL)
    with open(os.path.join(card, 'card-qr.svg'), 'w', encoding='utf-8') as f: f.write(qr.svg(m, title='farazisgiannis.com/card'))
    with open(os.path.join(card, 'card-qr.png'), 'wb') as f: f.write(qr.png(m, scale=24))
    urls = []
    for pid, fn in PAGES.items():
        for lang in ('el', 'en'):
            u = url(pid, lang); write(u.lstrip('/') + 'index.html', with_print_qr(fn(lang), u)); urls.append((pid, lang, u))
        if RU_ON:
            RENDER['ru'] = True
            try:
                u = url(pid, 'ru'); write(u.lstrip('/') + 'index.html', with_print_qr(ru_page(fn('en')), u)); urls.append((pid, 'ru', u))
            finally:
                RENDER['ru'] = False
    if RU_MISSING: print('Russian: not yet translated:', len(RU_MISSING), '→', sorted(RU_MISSING)[:8])
    for old, to in LEGACY.items(): write(f'{old}/index.html', redirect_page(to))
    write('404.html', with_print_qr(page_404(), '/'))
    if not PREFIX: write('CNAME', 'farazisgiannis.com\n')
    write('.nojekyll', '')
    # Search Console ownership file (URL-prefix property https://farazisgiannis.com/); keep it, or verification is lost
    write('google80208fabf8b37052.html', 'google-site-verification: google80208fabf8b37052.html')
    # Bing Webmaster Tools ownership file (same reason)
    write('BingSiteAuth.xml', '<?xml version="1.0"?>\n<users>\n\t<user>4DD6662B87831D9B870845ABE00172F7</user>\n</users>\n')
    # the preview must not be indexed (it would compete with the real address)
    # /preview/ holds the owner's preview of changes waiting for his approval (built from the preview branch, not indexed)
    write('robots.txt', 'User-agent: *\nDisallow: /\n' if PREFIX else f'User-agent: *\nAllow: /\nDisallow: /preview/\n\nSitemap: {BASE}/sitemap.xml\n')
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for pid, lang, u in urls:
        sm.append(f'<url><loc>{BASE}{u}</loc><lastmod>{ASSET_V}</lastmod>'
                  ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{url(pid, l)}"/>' for l in LANGS) + '</url>')
    sm.append('</urlset>')
    write('sitemap.xml', '\n'.join(sm) + '\n')
    write('llms.txt', f'''# Giannis Farazis — Insurance Advisor (Cyprus)

> Γιάννης Φαραζής (Ioannis Farazis), Insurance Advisor since 2024, based in Nicosia, serving clients across Cyprus in Greek and English.
> Life, health and accident cover, retirement and pension planning, savings and insurance-linked investment plans,
> children's education, loan protection, business and group insurance, and policy reviews.

- Phone (business mobile): {PHONE}
- Website: {BASE}/ (Greek), {BASE}/en/ (English)
- LinkedIn: {LINKEDIN}

## Pages
''' + ''.join(f'- [{L(T["nav"][p], "en") if p != "home" else "Home"}]({BASE}{url(p, "en")})\n' for p in PAGES) + '\nThe information on this website is general and is not personal advice.\n')
    print(f'built {len(urls)} pages + {len(LEGACY)} redirects into {OUT}')

if __name__ == '__main__':
    main()
