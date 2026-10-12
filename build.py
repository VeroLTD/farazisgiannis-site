#!/usr/bin/env python3
"""farazisgiannis.com — builds the static site (Greek at /, English at /en/) into ./site.

Content follows the owner's brief of 10 Oct 2026 (FARAZIS_GIANNIS_CLAUDE_WEBSITE_BRIEF_UPDATED_2026-10-10.md):
insurance work only; career since 2024; Nicosia, all of Cyprus; Greek and English; only the professional mobile
+357 97 840941 (office +357 22 124867 approved); Eurolife ONLY in the contact section; no e-mail published; the
contact form is e-mailed by the owner's own server (app.avrastro.com/v1/enquiry) and not stored; no analytics, no
cookies. Design v2 (owner feedback 10 Oct 22:25): full logo in the header (no name text beside it), a photo for every
topic (CC0 photos from the AVRASTRO library, assets/img/photos/CREDITS.md), richer layout in AVRASTRO's quality.
Run: python3 build.py  (no dependencies)
"""
import html, json, os, shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'site')
BASE = 'https://farazisgiannis.com'
UPDATED = '2026-10-10b'   # privacy page "last updated"
ASSET_V = '2026-10-11b'   # cache key of site.css / site.js, and the sitemap date (narrated films added 11 Oct 2026)
PHONE = '+357 97 840941'; TEL = '+35797840941'
OFFICE = '+357 22 124867'; OFFICE_TEL = '+35722124867'
WHATSAPP = 'https://wa.me/35797840941'
LINKEDIN = 'https://www.linkedin.com/in/giannis-farazis-209221350/'
AVRASTRO = 'https://avrastro.com'
ENQUIRY = 'https://app.avrastro.com/v1/enquiry'

SLUGS = {
    'home': {'el': '', 'en': ''},
    'about': {'el': 'sxetika', 'en': 'about'},
    'solutions': {'el': 'lyseis', 'en': 'solutions'},
    'how': {'el': 'pos-douleuo', 'en': 'how-i-work'},
    'guides': {'el': 'odigoi', 'en': 'guides'},
    'contact': {'el': 'epikoinonia', 'en': 'contact'},
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
    slug = SLUGS[page][lang]
    return ('/en/' if lang == 'en' else '/') + (slug + '/' if slug else '') + (('#' + anchor) if anchor else '')

ICON = {
    'phone': '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 3h3l2 5-2.5 1.5a11 11 0 0 0 7 7L16 14l5 2v3a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    'wa': '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20l1.3-3.8A8 8 0 1 1 8 19z"/><path d="M9 9.5c.3 2 2.2 4.2 4.5 4.8l1.2-1.1 1.8.8c-.2 1-1 1.8-2 1.8A6 6 0 0 1 8 9.8c0-1 .8-1.8 1.8-2l.8 1.8z"/></svg>',
    'clear': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M10 8h20l8 8v24H10z"/><path d="M30 8v8h8"/><path d="M16 24h16M16 30h16M16 36h10"/></svg>',
    'calm': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="24" cy="24" r="16"/><path d="M17 27c2 3 4.5 4.5 7 4.5s5-1.5 7-4.5"/><path d="M18 19h.01M30 19h.01" stroke-width="3" stroke-linecap="round"/></svg>',
    'with': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M24 40s-14-8.5-14-19a8 8 0 0 1 14-5.3A8 8 0 0 1 38 21c0 10.5-14 19-14 19z"/></svg>',
    'cy': '<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M24 42s13-12 13-23a13 13 0 0 0-26 0c0 11 13 23 13 23z"/><circle cx="24" cy="19" r="4.5"/></svg>',
    'check': '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 10.5l4 4 8-9"/></svg>',
    'arrow': '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 10h11M11 5l5 5-5 5"/></svg>',
}
LINES = ('<svg class="lines" viewBox="0 0 400 400" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2">'
         '<path d="M330 40H190A150 150 0 0 0 60 255"/><path d="M330 92H150"/><path d="M215 92 55 252"/>'
         '<path d="M330 190H180L40 330"/><path d="M220 190 80 330"/><path d="M262 214 168 308"/>'
         '<path d="M330 190A150 150 0 0 1 120 330"/></svg>')

def photo(key, alt='', cls='', eager=False):
    return (f'<img class="{cls}" src="/assets/img/photos/{key}.webp" width="900" height="600" alt="{esc(alt)}"'
            + ('' if eager else ' loading="lazy"') + ' decoding="async">')

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

# Narrated explainer films (11 Oct 2026), made in the AVRASTRO repository (tools/video) and copied here by
# tools/add_explainers.py: assets/video/explainers/explainers.json → {key: {lang: {video, poster, vtt, title, duration}}}
_EXP = os.path.join(ROOT, 'assets/video/explainers/explainers.json')
EXPLAINERS = json.load(open(_EXP, encoding='utf8')) if os.path.exists(_EXP) else {}
FILM_OF = {'life': 'topic-life', 'health': 'topic-health', 'accident': 'topic-income', 'retirement': 'topic-retirement',
           'savings': 'topic-savings', 'education': 'topic-education', 'business': 'topic-business', 'group': 'topic-group',
           'expats': 'topic-expats', 'loan': 'topic-loan', 'review': 'topic-review'}

def explainer(key, lang, cls=''):
    """A narrated film with its poster, captions (off until the visitor turns them on) and a large play button; it
    plays only when the visitor presses play. Empty when the film is not in the site yet."""
    e = EXPLAINERS.get(key, {}).get(lang)
    if not e:
        return ''
    v = '/assets/video/explainers/'
    el = lang == 'el'
    secs = int(round(e.get('duration', 0)))
    length = f'{secs // 60}:{secs % 60:02d}' if secs else ''
    play = ('Αναπαραγωγή βίντεο: ' if el else 'Play the video: ') + e['title']
    ld = {'@context': 'https://schema.org', '@type': 'VideoObject', 'name': e['title'], 'description': e.get('description') or e['title'],
          'thumbnailUrl': BASE + v + e['poster'], 'contentUrl': BASE + v + e['video'], 'uploadDate': e.get('date', ASSET_V[:10]),
          'duration': f'PT{secs // 60}M{secs % 60}S', 'inLanguage': lang}
    cc = f'<track kind="captions" src="{v}{e["vtt"]}" srclang="{lang}" label="{"Ελληνικά" if el else "English"}">' if e.get('vtt') else ''
    cap = f'<span class="explainer__title">{esc(e["title"])}</span>' + (f'<span>{length}</span>' if length else '') + (f'<span>{"Με υπότιτλους" if el else "Captions available"}</span>' if cc else '')
    return (f'<figure class="explainer {cls}"><div class="explainer__frame">'
            f'<video class="explainer__video" controls preload="none" playsinline width="1920" height="1080" poster="{v}{e["poster"]}" aria-label="{esc(e["title"])}">'
            f'<source src="{v}{e["video"]}" type="video/mp4">{cc}</video>'
            f'<button class="explainer__play" type="button" hidden aria-label="{esc(play)}"><span class="explainer__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg></span>'
            f'<span aria-hidden="true">{"Δείτε το βίντεο" if el else "Watch"}' + (f' <b>{length}</b>' if length else '') + '</span></button></div>'
            f'<figcaption>{cap}</figcaption>'
            '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script></figure>')

def portrait(alt='', cls='', eager=False):
    return (f'<picture><source srcset="/assets/img/giannis-farazis-portrait.webp" type="image/webp"><img class="{cls}" src="/assets/img/giannis-farazis-portrait.jpg" '
            f'width="480" height="600" alt="{esc(alt)}"' + (' fetchpriority="high"' if eager else ' loading="lazy"') + '></picture>')

def head(lang, page, title, desc, extra_ld=None):
    alt_lang = 'en' if lang == 'el' else 'el'
    canonical = BASE + url(page, lang)
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
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="el" href="{BASE + url(page, 'el')}">
<link rel="alternate" hreflang="en" href="{BASE + url(page, 'en')}">
<link rel="alternate" hreflang="x-default" href="{BASE + url(page, 'el')}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Giannis Farazis">
<meta property="og:locale" content="{'el_GR' if lang == 'el' else 'en_GB'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}/assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#142a4c">
<link rel="icon" href="/assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/GFSDidot-Regular.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ld[0], ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{L(T['skip'], lang)}</a>
<header class="site-head"><div class="wrap">
<a class="brand" href="{url('home', lang)}" aria-label="Giannis Farazis — {'Αρχική' if lang == 'el' else 'Home'}"><img src="/assets/img/gf-lockup.png" alt="Giannis Farazis — Mazi sou, kathe stigmi" width="294" height="70"></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">{L(T['menu'], lang)}</button>
<nav class="nav" id="nav" aria-label="{'Κύριο μενού' if lang == 'el' else 'Main menu'}">
{navlinks}
<a class="lang" href="{url(page, alt_lang)}" hreflang="{alt_lang}" lang="{alt_lang}">{L(T['other'], lang)}</a>
<a class="nav-call" href="tel:{TEL}">{ICON['phone']}{PHONE}</a>
</nav></div></header>
<main id="main">
'''

def foot(lang):
    el = lang == 'el'
    return f'''</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-brand"><img src="/assets/img/gf-logo.png" alt="Giannis Farazis — Mazi sou, kathe stigmi" width="200" height="115" loading="lazy">
<p>{L(T['foot'], lang)}</p></div>
<div class="foot-col"><h2>{'Σελίδες' if el else 'Pages'}</h2>{''.join(f'<a href="{url(p, lang)}">{L(T["nav"][p], lang)}</a>' for p in NAV + ['privacy'])}</div>
<div class="foot-col"><h2>{'Επικοινωνία' if el else 'Contact'}</h2>
<a href="tel:{TEL}">{PHONE}</a><a href="{WHATSAPP}" rel="noopener">WhatsApp</a><a href="{LINKEDIN}" rel="noopener">LinkedIn</a>
<span>{'Λευκωσία · Παγκύπρια' if el else 'Nicosia · all of Cyprus'}</span></div>
</div><div class="wrap foot-legal">© {date.today().year} {L(T['name'], lang)}</div></footer>
<div class="callbar"><a href="tel:{TEL}">{ICON['phone']}{L(T['call'], lang)}</a><a href="{WHATSAPP}" rel="noopener">{ICON['wa']}WhatsApp</a></div>
<script src="/assets/js/site.js?v={ASSET_V}" defer></script>
</body></html>
'''

def actions(lang, extra=''):
    return f'''<div class="actions">
<a class="btn btn-primary" href="tel:{TEL}">{ICON['phone']}{L(T['call'], lang)} {PHONE}</a>
<a class="btn btn-ghost" href="{WHATSAPP}" rel="noopener">{ICON['wa']}WhatsApp</a>{extra}
</div>'''

def page_head(title, lead, img=None, alt='', movie=None, lang='el'):
    media = (f'<figure class="page-head__media">{film(movie, lang)}</figure>' if movie
             else f'<figure class="page-head__media">{photo(img, alt, eager=True)}</figure>' if img else '')
    return f'<section class="page-head{" has-media" if (img or movie) else ""}"><div class="wrap"><div class="page-head__text"><h1>{title}</h1><p>{lead}</p></div>{media}</div></section>'

def cta_band(lang):
    el = lang == 'el'
    return f'''<section class="cta-band on-dark"><div class="wrap">
<div class="cta-band__photo">{portrait('')}</div>
<div><h2>{'Μια πρώτη συζήτηση, χωρίς δέσμευση' if el else 'A first conversation, with no commitment'}</h2>
<p>{'Καλέστε, στείλτε μήνυμα στο WhatsApp ή αφήστε τα στοιχεία σας και θα σας καλέσω εγώ.' if el else 'Call, send a WhatsApp message, or leave your details and I will call you.'}</p>
{actions(lang, f'<a class="btn btn-link" href="{url("contact", lang)}">{"Φόρμα επικοινωνίας" if el else "Contact form"}{ICON["arrow"]}</a>')}</div>
</div></section>'''

# ------------------------------------------------------------------ content
# (id, photo, title, short, long, includes[], question)
SOLUTIONS = [
    ('life', 'life',
     {'el': 'Ασφάλεια ζωής', 'en': 'Life insurance'},
     {'el': 'Ένα ποσό για τους ανθρώπους σας αν δεν είστε εκεί.', 'en': 'A sum for the people you love if you are not there.'},
     {'el': 'Η ασφάλεια ζωής πληρώνει ένα ποσό στους δικαιούχους που ορίζετε. Μπορεί να εξοφλήσει ένα δάνειο, να αντικαταστήσει για κάποια χρόνια το εισόδημα που χάνεται και να κρατήσει όρθιους τους στόχους της οικογένειας, όπως τις σπουδές των παιδιών.',
      'en': 'Life insurance pays a sum to the beneficiaries you choose. It can pay off a loan, replace lost income for a number of years and keep your family’s plans on track, such as the children’s studies.'},
     [{'el': 'Κάλυψη για συγκεκριμένα χρόνια ή για όλη τη ζωή', 'en': 'Cover for a set number of years, or for life'},
      {'el': 'Πρόσθετες καλύψεις, όπως σοβαρές ασθένειες ή ανικανότητα', 'en': 'Extra cover such as serious illness or disability'},
      {'el': 'Δικαιούχους που αλλάζετε όταν αλλάζει η ζωή σας', 'en': 'Beneficiaries you can change as your life changes'}],
     {'el': 'Πόσο κεφάλαιο και για πόσα χρόνια χρειάζεται η δική σας οικογένεια;', 'en': 'How much cover, and for how many years, does your family need?'}),
    ('health', 'health',
     {'el': 'Ιατροφαρμακευτική κάλυψη', 'en': 'Health and medical cover'},
     {'el': 'Ένα ιδιωτικό σχέδιο δίπλα στο ΓεΣΥ.', 'en': 'A private plan alongside GESY.'},
     {'el': 'Το ΓεΣΥ καλύπτει πολλά, όχι όμως τα πάντα. Ένα ιδιωτικό σχέδιο υγείας το συμπληρώνει, όταν θέλετε θεραπεία εκτός ΓεΣΥ, ιδιωτικό δωμάτιο, ευελιξία στον χρόνο ή κάλυψη στο εξωτερικό.',
      'en': 'GESY covers a great deal, but not everything. A private health plan complements it when you want treatment outside GESY, a private room, flexibility over timing, or cover abroad.'},
     [{'el': 'Νοσηλεία και επεμβάσεις', 'en': 'Hospital stays and operations'},
      {'el': 'Εξωνοσοκομειακά έξοδα, ανάλογα με το σχέδιο', 'en': 'Outpatient costs, depending on the plan'},
      {'el': 'Θεραπεία στο εξωτερικό, ανάλογα με το σχέδιο', 'en': 'Treatment abroad, depending on the plan'}],
     {'el': 'Τι μένει ακάλυπτο σήμερα και πόσο κοστίζει να το καλύψετε;', 'en': 'What is left uncovered today, and what would it cost to cover it?'}),
    ('accident', 'accident',
     {'el': 'Προσωπικό ατύχημα', 'en': 'Personal accident'},
     {'el': 'Προστασία για τραυματισμό και για το εισόδημα που χάνεται.', 'en': 'Protection for injury, and for the income you lose.'},
     {'el': 'Ένα ατύχημα μπορεί να σταματήσει τη δουλειά για εβδομάδες ή μήνες. Η ασφάλεια προσωπικού ατυχήματος δίνει ποσά για τραυματισμό ή αναπηρία και, ανάλογα με το σχέδιο, ένα επίδομα όσο δεν μπορείτε να εργαστείτε.',
      'en': 'An accident can stop you working for weeks or months. Personal accident cover pays sums for injury or disability and, depending on the plan, an allowance while you cannot work.'},
     [{'el': 'Ποσό για μόνιμη αναπηρία από ατύχημα', 'en': 'A sum for permanent disability from an accident'},
      {'el': 'Επίδομα όσο δεν εργάζεστε, ανάλογα με το σχέδιο', 'en': 'An allowance while you cannot work, depending on the plan'},
      {'el': 'Ιατρικά έξοδα από ατύχημα', 'en': 'Medical costs from an accident'}],
     {'el': 'Πώς θα πληρώνατε τα έξοδα αν σταματούσατε να εργάζεστε για μερικούς μήνες;', 'en': 'How would you pay your bills if you stopped working for a few months?'}),
    ('retirement', 'retirement',
     {'el': 'Σύνταξη', 'en': 'Retirement and pension planning'},
     {'el': 'Τακτική αποταμίευση για τα χρόνια μετά τη δουλειά.', 'en': 'Regular saving for the years after work.'},
     {'el': 'Η σύνταξη των Κοινωνικών Ασφαλίσεων σπάνια φτάνει για τη ζωή που θέλετε. Ένα συνταξιοδοτικό πρόγραμμα χτίζει σταδιακά ένα κεφάλαιο, και όσο νωρίτερα ξεκινάτε τόσο μικρότερο είναι το ποσό που χρειάζεται κάθε μήνα.',
      'en': 'A Social Insurance pension rarely covers the life you want. A pension plan builds up capital over time, and the earlier you start, the smaller the monthly amount you need.'},
     [{'el': 'Μηνιαία ή ετήσια καταβολή', 'en': 'Monthly or yearly contributions'},
      {'el': 'Κεφάλαιο ή τακτικό εισόδημα στη σύνταξη', 'en': 'A lump sum or regular income in retirement'},
      {'el': 'Φορολογική έκπτωση, όπου ισχύει', 'en': 'Tax relief, where it applies'}],
     {'el': 'Πόσο εισόδημα θέλετε στη σύνταξη και πόσο λείπει;', 'en': 'How much income do you want in retirement, and how much is missing?'}),
    ('savings', 'savings',
     {'el': 'Αποταμίευση και επενδυτικά προγράμματα', 'en': 'Savings and investment-linked plans'},
     {'el': 'Μακροπρόθεσμη αποταμίευση με στόχο.', 'en': 'Long-term saving towards a goal.'},
     {'el': 'Τακτική αποταμίευση για έναν στόχο που απέχει χρόνια: ένα κεφάλαιο, ένα σπίτι, ένα μαξιλάρι ασφαλείας. Στα επενδυτικά προγράμματα η αξία ανεβαίνει και κατεβαίνει και δεν είναι εγγυημένη· το εξηγούμε καθαρά πριν αποφασίσετε.',
      'en': 'Regular saving for a goal that is years away: capital, a home, a safety cushion. In investment-linked plans the value goes up and down and is not guaranteed; we go through this clearly before you decide.'},
     [{'el': 'Στόχος και ορίζοντας χρόνου που ορίζετε εσείς', 'en': 'A goal and time horizon you set'},
      {'el': 'Επιλογή επιπέδου κινδύνου', 'en': 'A choice of risk level'},
      {'el': 'Συχνά με κάλυψη ζωής', 'en': 'Often with life cover included'}],
     {'el': 'Για πόσα χρόνια μπορείτε να αφήσετε τα χρήματα και πόσο ρίσκο αντέχετε;', 'en': 'For how many years can you leave the money, and how much risk can you live with?'}),
    ('education', 'education',
     {'el': 'Παιδί και σπουδές', 'en': 'Children and education'},
     {'el': 'Το ποσό των σπουδών, έτοιμο όταν χρειαστεί.', 'en': 'The cost of studies, ready when it is needed.'},
     {'el': 'Ένα σχέδιο που μαζεύει σταδιακά το ποσό των σπουδών μέχρι την ηλικία που θα το χρειαστεί το παιδί. Συνήθως περιλαμβάνει κάλυψη του γονιού, ώστε το πλάνο να συνεχίζεται αν συμβεί κάτι.',
      'en': 'A plan that gradually builds up the cost of studies by the age your child will need it. It usually includes cover on the parent, so the plan carries on if something happens.'},
     [{'el': 'Κεφάλαιο στην ηλικία των σπουδών', 'en': 'Capital at the age of study'},
      {'el': 'Συνέχιση του πλάνου αν συμβεί κάτι στον γονιό', 'en': 'The plan carries on if something happens to the parent'},
      {'el': 'Για γονείς, παππούδες και νονούς', 'en': 'For parents, grandparents and godparents'}],
     {'el': 'Πόσα χρόνια έχετε μέχρι το πανεπιστήμιο και τι θα κοστίσει;', 'en': 'How many years until university, and what will it cost?'}),
    ('loan', 'loan',
     {'el': 'Προστασία δανείου', 'en': 'Loan protection'},
     {'el': 'Το σπίτι μένει στην οικογένεια, όχι το χρέος.', 'en': 'Your family keeps the home, not the debt.'},
     {'el': 'Για ένα στεγαστικό δάνειο η τράπεζα ζητά συνήθως ασφάλεια ζωής. Βλέπουμε μαζί αν η κάλυψη ταιριάζει με το υπόλοιπο και τη διάρκεια του δανείου, και αν χρειάζεται κάτι επιπλέον για το εισόδημα της οικογένειας.',
      'en': 'For a mortgage the bank usually asks for life cover. We check together whether the cover matches the balance and term of the loan, and whether your family’s income needs something more.'},
     [{'el': 'Κεφάλαιο ίσο με το υπόλοιπο του δανείου', 'en': 'Cover that matches the loan balance'},
      {'el': 'Εκχώρηση στην τράπεζα', 'en': 'Assignment to the bank'},
      {'el': 'Επανεξέταση όταν αλλάζει το δάνειο', 'en': 'A review when the loan changes'}],
     {'el': 'Καλύπτει η τωρινή σας ασφάλεια ολόκληρο το υπόλοιπο του δανείου;', 'en': 'Does your current cover match the full balance of the loan?'}),
    ('business', 'business',
     {'el': 'Προστασία επιχείρησης', 'en': 'Business protection'},
     {'el': 'Για τους ανθρώπους που κρατούν την επιχείρηση όρθια.', 'en': 'For the people who keep the business going.'},
     {'el': 'Σε πολλές επιχειρήσεις ένας ή δύο άνθρωποι φέρνουν το μεγαλύτερο μέρος των εσόδων. Η ασφάλεια βασικού στελέχους βοηθά να καλυφθούν τα χαμένα έσοδα και το κόστος αντικατάστασης αν λείψει ένα πρόσωπο-κλειδί. Η προστασία συνεταίρων, μαζί με γραπτή συμφωνία, επιτρέπει σε όσους μένουν να αγοράσουν το μερίδιο χωρίς να πουληθεί η επιχείρηση.',
      'en': 'In many businesses one or two people bring in most of the revenue. Key person insurance helps cover lost revenue and the cost of replacing someone critical. Partner protection, with a written agreement, lets the remaining partners buy the share without selling the business.'},
     [{'el': 'Ασφάλεια βασικού στελέχους', 'en': 'Key person insurance'},
      {'el': 'Προστασία συνεταίρων και μετόχων', 'en': 'Partner and shareholder protection'},
      {'el': 'Λύσεις για αυτοεργοδοτούμενους', 'en': 'Options for the self-employed'}],
     {'el': 'Τι θα γινόταν στην επιχείρηση αν έλειπε ένα βασικό πρόσωπο;', 'en': 'What would happen to the business if a key person were missing?'}),
    ('group', 'business',
     {'el': 'Ομαδικά σχέδια για εταιρείες', 'en': 'Group plans for companies'},
     {'el': 'Παροχές που βοηθούν να κρατήσετε καλούς ανθρώπους.', 'en': 'Benefits that help you keep good people.'},
     {'el': 'Ομαδικό σχέδιο υγείας που συμπληρώνει το ΓεΣΥ, ομαδική ασφάλεια ζωής και ατυχημάτων με ενιαίους όρους για όλους, και ταμείο προνοίας με εισφορές εργοδότη και εργαζομένου. Τα σχεδιάζουμε με βάση το μέγεθος, τις ηλικίες και τον προϋπολογισμό της ομάδας σας.',
      'en': 'A group health plan that complements GESY, group life and accident cover with one set of terms for everyone, and a provident fund with employer and employee contributions. We shape them around the size, ages and budget of your team.'},
     [{'el': 'Ομαδικό ιατροφαρμακευτικό σχέδιο', 'en': 'Group health plan'},
      {'el': 'Ομαδική ασφάλεια ζωής και ατυχημάτων', 'en': 'Group life and accident cover'},
      {'el': 'Ταμείο προνοίας ή ομαδικό συνταξιοδοτικό σχέδιο', 'en': 'Provident fund or group pension'}],
     {'el': 'Πόσα άτομα θέλετε να καλύψετε, και τι μπορεί να διαθέσει η επιχείρηση ανά εργαζόμενο;', 'en': 'How many people do you want to cover, and what can the business spend per employee?'}),
    ('expats', 'health',
     {'el': 'Για ξένους κατοίκους', 'en': 'For expats in Cyprus'},
     {'el': 'Υγεία, άδεια διαμονής, δάνειο και σύνταξη, και στα Αγγλικά.', 'en': 'Health, residence permits, mortgages and pensions, in English.'},
     {'el': 'Αν μετακομίσατε στην Κύπρο, το σύστημα μπορεί να διαφέρει από αυτό που ξέρετε. Βλέπουμε μαζί αν δικαιούστε ΓεΣΥ, την ιδιωτική ασφάλεια υγείας που ζητά συχνά η άδεια διαμονής, την ασφάλεια ζωής για το στεγαστικό δάνειο και τη σύνταξή σας.',
      'en': 'If you have moved to Cyprus, the system may be quite different from what you know. We look together at whether you are entitled to GESY, the private health cover residence permits often ask for, life cover for your mortgage, and your pension.'},
     [{'el': 'Ιδιωτική ασφάλεια υγείας για την άδεια διαμονής', 'en': 'Private health cover for your residence permit'},
      {'el': 'Ασφάλεια ζωής για στεγαστικό δάνειο', 'en': 'Life cover for your mortgage'},
      {'el': 'Σχεδιασμός σύνταξης', 'en': 'Retirement planning'}],
     {'el': 'Ποια άδεια διαμονής έχετε ή ζητάτε, και τι ακριβώς απαιτεί;', 'en': 'Which residence permit do you hold or need, and what exactly does it require?'}),
    ('review', 'review',
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
    ('step-talk', {'el': 'Μια πρώτη συζήτηση', 'en': 'A first conversation'},
     {'el': 'Τηλεφωνικά, με βιντεοκλήση ή από κοντά. Ακούω τι θέλετε να προστατεύσετε και τι έχετε ήδη.', 'en': 'By phone, video call or in person. I listen to what you want to protect and what you already have.'}),
    ('step-needs', {'el': 'Ανάλυση αναγκών', 'en': 'Looking at your needs'},
     {'el': 'Βλέπουμε μαζί οικογένεια, εισόδημα, δάνεια και στόχους, και πού βρίσκονται τα κενά.', 'en': 'Together we look at family, income, loans and goals, and where the gaps are.'}),
    ('step-proposal', {'el': 'Πρόταση με απλά λόγια', 'en': 'A proposal in plain words'},
     {'el': 'Τι καλύπτει, τι δεν καλύπτει και πόσο κοστίζει. Χωρίς πίεση για απόφαση την ίδια μέρα.', 'en': 'What it covers, what it does not and what it costs. No pressure to decide on the day.'}),
    ('step-after', {'el': 'Δίπλα σας και μετά', 'en': 'With you afterwards'},
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
    ('gesy', 'guide-health', {'el': 'ΓεΣΥ και ιδιωτικό σχέδιο υγείας', 'en': 'GESY and a private health plan'},
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

def sol_cards(lang, items=SOLUTIONS):
    return '<ul class="cards">' + ''.join(
        f'<li class="card"><a href="{url("solutions", lang, sid)}"><figure>{photo(img, "")}</figure>'
        f'<h3>{L(t, lang)}</h3><p>{L(s, lang)}</p><span class="card__more">{L(T["more"], lang)}{ICON["arrow"]}</span></a></li>'
        for sid, img, t, s, *_ in items) + '</ul>'

def values_grid(lang):
    return '<ul class="values">' + ''.join(f'<li><span class="values__icon">{ICON[i]}</span><h3>{L(t, lang)}</h3><p>{L(d, lang)}</p></li>' for i, t, d in VALUES) + '</ul>'

def steps_grid(lang):
    return '<ol class="stepcards">' + ''.join(
        f'<li><figure>{photo(img, "")}</figure><div><h3>{L(t, lang)}</h3><p>{L(d, lang)}</p></div></li>' for img, t, d in STEPS) + '</ol>'

def page_home(lang):
    el = lang == 'el'
    title = 'Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος στη Λευκωσία' if el else 'Giannis Farazis, Insurance Advisor in Nicosia, Cyprus'
    desc = ('Ασφάλεια ζωής, υγείας, σύνταξη, αποταμίευση και σπουδές παιδιών. Προσωπική καθοδήγηση σε όλη την Κύπρο, στα Ελληνικά και Αγγλικά. +357 97 840941.' if el
            else 'Life and health cover, retirement, savings and children’s education. Personal guidance across Cyprus, in Greek and English. +357 97 840941.')
    guides = '<ul class="cards cards--3">' + ''.join(
        f'<li class="card"><a href="{url("guides", lang, gid)}"><figure>{photo(img, "")}</figure><h3>{L(t, lang)}</h3><p>{L(s, lang)}</p><span class="card__more">{L(T["more"], lang)}{ICON["arrow"]}</span></a></li>'
        for gid, img, t, s, _ in GUIDES) + '</ul>'
    # "A few words about me": the short narrated introduction when it is on the site, otherwise the portrait
    meet = explainer('meet-giannis', lang)
    about_film_cls = ' split--film' if meet else ''
    about_media = f'<div class="split__film">{meet}</div>' if meet else f'<figure class="split__photo">{portrait("")}</figure>'
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

<section class="section tint"><div class="wrap split{about_film_cls}">
{about_media}
<div><hr class="rule">
<h2>{'Λίγα λόγια για μένα' if el else 'A few words about me'}</h2>
<p>{'Είμαι Ασφαλιστικός Σύμβουλος από το 2024, με βάση τη Λευκωσία, και εξυπηρετώ πελάτες σε όλη την Κύπρο, στα Ελληνικά και στα Αγγλικά. Πιστεύω ότι η ασφάλιση δεν είναι απλώς ένα προϊόν· είναι ένα εργαλείο για να σχεδιάσει κανείς με ηρεμία το μέλλον του.' if el else 'I have been an Insurance Advisor since 2024. I am based in Nicosia and work with clients across Cyprus, in Greek and English. I believe insurance is not just a product; it is a way to plan your future calmly.'}</p>
<p>{'Για μένα κάθε πελάτης είναι ξεχωριστός. Ξεκινάμε από τις δικές σας ανάγκες και προχωράμε μόνο όταν όλα είναι ξεκάθαρα.' if el else 'Every client is different. We start from your needs and only go ahead once everything is clear.'}</p>
<p><a class="btn btn-ghost" href="{url('about', lang)}">{'Περισσότερα για μένα' if el else 'More about me'}</a></p>
</div></div></section>

<section class="section"><div class="wrap">
<div class="section-head"><hr class="rule"><h2>{'Χρήσιμοι οδηγοί' if el else 'Helpful guides'}</h2>
<p class="lead">{'Σύντομες απαντήσεις στις ερωτήσεις που ακούω πιο συχνά.' if el else 'Short answers to the questions I hear most often.'}</p></div>
{guides}
</div></section>
''' + cta_band(lang) + foot(lang)

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
    meet = explainer('meet-giannis', lang, 'explainer--wide')
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
<figure class="portrait portrait--sm">{LINES}{portrait('Ο Γιάννης Φαραζής' if el else 'Giannis Farazis', eager=True)}</figure>
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
        fm = explainer(FILM_OF.get(sid, ''), lang)   # the subject's narrated film in place of its photo, when there is one
        media = fm or f'<figure>{photo(img, "")}</figure>'
        rows += f'''<article class="sol{' is-reverse' if i % 2 else ''}{' has-film' if fm else ''}" id="{sid}">
{media}
<div><h2>{L(t, lang)}</h2><p class="sol__short">{L(s, lang)}</p><p>{L(lng, lang)}</p>
<h3>{'Μπορεί να περιλαμβάνει' if el else 'It can include'}</h3>
<ul class="ticks">{''.join(f'<li>{ICON["check"]}{L(x, lang)}</li>' for x in inc)}</ul>
<p class="ask"><span>{'Η ερώτηση που ξεκινάμε' if el else 'Where we start'}</span>{L(q, lang)}</p>
</div></article>'''
    note = ('Κάθε πρόταση βασίζεται στους όρους του συγκεκριμένου συμβολαίου. Οι καλύψεις έχουν όρια, εξαιρέσεις και, όπου ισχύει, περιόδους αναμονής, που τα βλέπουμε μαζί πριν υπογράψετε. Οι αποδόσεις των επενδυτικών προγραμμάτων δεν είναι εγγυημένες, και η φορολογική έκπτωση εξαρτάται από την προσωπική σας περίπτωση.' if el
            else 'Every proposal is based on the terms of the specific policy. Cover has limits, exclusions and, where they apply, waiting periods, which we go through together before you sign. Returns on investment-linked plans are not guaranteed, and tax relief depends on your own circumstances.')
    return head(lang, 'solutions', title, desc) + page_head(L(T['nav']['solutions'], lang),
        'Έντεκα ανάγκες που βλέπουμε μαζί. Ξεκινάμε πάντα από μια απλή ερώτηση.' if el else 'Eleven needs we look at together. We always start with one simple question.', 'life', '', 'film-solutions', lang) + f'''
<section class="section section--tight"><div class="wrap">{jump}{rows}<p class="note">{note}</p></div></section>''' + cta_band(lang) + foot(lang)

def page_how(lang):
    el = lang == 'el'
    title = 'Πώς δουλεύω: από την πρώτη συζήτηση στην αποζημίωση' if el else 'How I work: from the first conversation to a claim'
    desc = 'Πρώτη συζήτηση, ανάλυση αναγκών, πρόταση με απλά λόγια και υποστήριξη μετά την υπογραφή. Τι να έχετε έτοιμο πριν μιλήσουμε.' if el else 'A first conversation, a look at your needs, a proposal in plain words, and support after you sign. What to have ready before we talk.'
    prep = (['Τι θέλετε να προστατεύσετε περισσότερο: οικογένεια, εισόδημα, υγεία, σπίτι ή σύνταξη.', 'Αν υπάρχει δάνειο ή άλλη μεγάλη υποχρέωση, και για πόσα χρόνια.', 'Τα συμβόλαια που ήδη έχετε: τουλάχιστον το είδος, την εταιρεία και το ασφάλιστρο.', 'Ένα κατά προσέγγιση μηνιαίο εισόδημα και τα βασικά έξοδα του σπιτιού.'] if el
            else ['What you most want to protect: family, income, health, home or retirement.', 'Whether there is a loan or other big commitment, and for how many years.', 'The policies you already have: at least the type, the insurer and the premium.', 'A rough monthly income and the household’s main costs.'])
    rows = ''.join(f'''<article class="sol{' is-reverse' if i % 2 else ''}"><figure>{photo(img, '')}</figure>
<div><p class="sol__step">{('Βήμα ' if el else 'Step ')}{i + 1}</p><h2>{L(t, lang)}</h2><p>{L(d, lang)}</p></div></article>''' for i, (img, t, d) in enumerate(STEPS))
    return head(lang, 'how', title, desc) + page_head(L(T['nav']['how'], lang), 'Τέσσερα βήματα, χωρίς βιασύνη και χωρίς ψιλά γράμματα.' if el else 'Four steps, with no rush and no small print.', 'step-talk', '', 'film-how', lang) + f'''
<section class="section section--tight"><div class="wrap">{rows}</div></section>
<section class="section tint"><div class="wrap split split--wide">
<figure class="split__img">{photo('about-work', '')}</figure>
<div><hr class="rule"><h2>{'Πριν μιλήσουμε' if el else 'Before we talk'}</h2>
<p>{'Δεν χρειάζεται να έχετε τα πάντα έτοιμα. Αν όμως σκεφτείτε από πριν τα παρακάτω, η συζήτηση θα είναι πιο σύντομη και πιο χρήσιμη.' if el else 'You do not need everything ready. But if you think about these beforehand, the conversation will be shorter and more useful.'}</p>
<ul class="ticks">{''.join(f'<li>{ICON["check"]}{x}</li>' for x in prep)}</ul>
<p class="note">{'Μη στέλνετε ιατρικά στοιχεία ή αριθμούς λογαριασμών μέσω της φόρμας. Αν χρειαστεί, τα συζητάμε με ασφαλή τρόπο.' if el else 'Please do not send medical details or account numbers through the form. If needed, we discuss them securely.'}</p>
</div></div></section>''' + cta_band(lang) + foot(lang)

def page_guides(lang):
    el = lang == 'el'
    title = 'Χρήσιμοι οδηγοί ασφάλισης για την Κύπρο' if el else 'Helpful insurance guides for Cyprus'
    desc = 'Πόση ασφάλεια ζωής χρειάζεστε, ΓεΣΥ και ιδιωτικό σχέδιο υγείας, και πότε να επανεξετάσετε τα συμβόλαιά σας.' if el else 'How much life cover you need, GESY and private health plans, and when to review your policies.'
    body = ''.join(f'''<article class="guide" id="{gid}"><figure>{photo(img, '')}</figure><div class="prose"><h2>{L(t, lang)}</h2><p class="sol__short">{L(s, lang)}</p>{L(b, lang)}</div></article>''' for gid, img, t, s, b in GUIDES)
    more = (f'<p>Για περισσότερους οδηγούς και δωρεάν υπολογιστές, δείτε το <a href="{AVRASTRO}/guides/" rel="noopener">AVRASTRO</a>, την ενημερωτική πλατφόρμα που δημιούργησα.</p>' if el
            else f'<p>For more guides and free calculators, see <a href="{AVRASTRO}/en/guides/" rel="noopener">AVRASTRO</a>, the information platform I created.</p>')
    src = ('Πηγή για τη φορολογική έκπτωση: PwC Worldwide Tax Summaries – Cyprus (Οκτώβριος 2026). Οι οδηγοί είναι γενική ενημέρωση και όχι εξατομικευμένη συμβουλή.' if el
           else 'Source for tax relief: PwC Worldwide Tax Summaries – Cyprus (October 2026). The guides are general information, not personal advice.')
    return head(lang, 'guides', title, desc) + page_head(L(T['nav']['guides'], lang), 'Σύντομες απαντήσεις στις ερωτήσεις που ακούω πιο συχνά.' if el else 'Short answers to the questions I hear most often.', 'guide-life', '', 'film-guides', lang) + f'''
<section class="section section--tight"><div class="wrap">{body}<div class="prose"><p class="note">{src}</p>{more}</div></div></section>''' + cta_band(lang) + foot(lang)

def page_contact(lang):
    title = {'el': 'Επικοινωνία: Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος', 'en': 'Contact Giannis Farazis, Insurance Advisor'}[lang]
    desc = {'el': 'Κινητό +357 97 840941, γραφείο +357 22 124867, WhatsApp ή φόρμα επικοινωνίας. Εξυπηρέτηση σε όλη την Κύπρο, Ελληνικά και Αγγλικά.', 'en': 'Mobile +357 97 840941, office +357 22 124867, WhatsApp or the contact form. Serving clients across Cyprus, in Greek and English.'}[lang]
    topics = {'el': ['Ασφάλεια ζωής', 'Υγεία', 'Ατύχημα', 'Σύνταξη', 'Αποταμίευση / επενδυτικά', 'Παιδί και σπουδές', 'Προστασία δανείου', 'Επιχείρηση / ομαδικά', 'Επανεξέταση συμβολαίων', 'Κάτι άλλο'],
              'en': ['Life insurance', 'Health', 'Accident', 'Retirement', 'Savings / investment-linked', 'Children and education', 'Loan protection', 'Business / group', 'Policy review', 'Something else']}[lang]
    opts = ''.join(f'<option>{esc(t)}</option>' for t in topics)
    el = lang == 'el'
    return head(lang, 'contact', title, desc) + page_head(L(T['nav']['contact'], lang), 'Μια πρώτη συζήτηση, χωρίς δέσμευση.' if el else 'A first conversation, with no commitment.') + f'''
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
</div></section>''' + foot(lang)

def page_privacy(lang):
    el = lang == 'el'
    title = 'Πολιτική απορρήτου' if el else 'Privacy policy'
    desc = 'Ποια στοιχεία συλλέγει η φόρμα επικοινωνίας, γιατί, για πόσο, και τα δικαιώματά σας. Χωρίς cookies και χωρίς εργαλεία παρακολούθησης.' if el else 'What the contact form collects, why, for how long, and your rights. No cookies and no tracking tools.'
    body = '''<p>Υπεύθυνος επεξεργασίας είναι ο Γιάννης Φαραζής, Ασφαλιστικός Σύμβουλος, Λευκωσία (τηλ. +357 97 840941).</p>
<h2>Τι συλλέγουμε και γιατί</h2>
<p>Μόνο ό,τι γράφετε στη φόρμα επικοινωνίας: ονοματεπώνυμο, τηλέφωνο ή e-mail, θέμα και μήνυμα. Τα χρησιμοποιούμε μόνο για να απαντήσουμε στο αίτημά σας. Νομική βάση είναι η συγκατάθεσή σας και τα βήματα που ζητάτε πριν από μια πιθανή σύμβαση.</p>
<h2>Πώς ταξιδεύουν τα στοιχεία</h2>
<p>Η φόρμα στέλνει το μήνυμα μέσω διακομιστή μας στην Ευρωπαϊκή Ένωση (Hetzner, Φινλανδία), ο οποίος το προωθεί με e-mail στο επαγγελματικό γραμματοκιβώτιο του συμβούλου και δεν το αποθηκεύει. Ο ιστότοπος φιλοξενείται στο GitHub Pages (GitHub Inc.), που μπορεί να καταγράφει τεχνικά στοιχεία όπως τη διεύθυνση IP για λόγους ασφάλειας.</p>
<h2>Για πόσο τα κρατάμε</h2>
<p>Όσο χρειάζεται για να απαντήσουμε και να εξυπηρετήσουμε το αίτημά σας. Αν δεν προχωρήσει συνεργασία, το μήνυμα διαγράφεται μέσα σε 12 μήνες.</p>
<h2>Cookies και στατιστικά</h2>
<p>Ο ιστότοπος δεν χρησιμοποιεί cookies, Google Analytics ή άλλα εργαλεία παρακολούθησης, και δεν φορτώνει γραμματοσειρές ή σενάρια από τρίτους.</p>
<h2>Τα δικαιώματά σας</h2>
<p>Μπορείτε να ζητήσετε πρόσβαση, διόρθωση ή διαγραφή των στοιχείων σας, να ανακαλέσετε τη συγκατάθεσή σας ή να αντιταχθείτε στην επεξεργασία, καλώντας στο +357 97 840941. Μπορείτε επίσης να υποβάλετε καταγγελία στον Επίτροπο Προστασίας Δεδομένων Προσωπικού Χαρακτήρα (<a href="https://www.dataprotection.gov.cy/" rel="noopener">www.dataprotection.gov.cy</a>).</p>''' if el else '''<p>The controller is Giannis Farazis, Insurance Advisor, Nicosia (tel. +357 97 840941).</p>
<h2>What we collect and why</h2>
<p>Only what you write in the contact form: your name, phone or e-mail, topic and message. We use it only to reply to your request. The legal basis is your consent and the steps you ask for before a possible contract.</p>
<h2>How your details travel</h2>
<p>The form sends your message through our server in the European Union (Hetzner, Finland), which forwards it by e-mail to the advisor’s business mailbox and does not store it. The website is hosted on GitHub Pages (GitHub Inc.), which may log technical data such as IP addresses for security.</p>
<h2>How long we keep it</h2>
<p>As long as needed to reply and deal with your request. If no business follows, the message is deleted within 12 months.</p>
<h2>Cookies and statistics</h2>
<p>This website uses no cookies, no Google Analytics and no other tracking tools, and loads no fonts or scripts from third parties.</p>
<h2>Your rights</h2>
<p>You can ask for access to, correction or erasure of your details, withdraw your consent or object to processing by calling +357 97 840941. You can also complain to the Cyprus Commissioner for Personal Data Protection (<a href="https://www.dataprotection.gov.cy/" rel="noopener">www.dataprotection.gov.cy</a>).</p>'''
    upd = f'<p class="note">{"Τελευταία ενημέρωση" if el else "Last updated"}: {UPDATED}</p>'
    return head(lang, 'privacy', title, desc) + page_head(title, desc) + f'<section class="section"><div class="wrap prose">{body}{upd}</div></section>' + foot(lang)

def redirect_page(to):
    return f'<!doctype html><html lang="el"><head><meta charset="utf-8"><title>Giannis Farazis</title><link rel="canonical" href="{BASE}{to}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={to}"></head><body><p><a href="{to}">farazisgiannis.com{to}</a></p></body></html>\n'

def page_404():
    return (head('el', 'home', 'Η σελίδα δεν βρέθηκε | Giannis Farazis', 'Η σελίδα δεν βρέθηκε.').replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')
            + page_head('Η σελίδα δεν βρέθηκε', 'Page not found') + f'<section class="section"><div class="wrap"><p><a href="/">Αρχική</a> · <a href="/en/">Home</a></p>{actions("el")}</div></section>' + foot('el'))

PAGES = {'home': page_home, 'about': page_about, 'solutions': page_solutions, 'how': page_how, 'guides': page_guides, 'contact': page_contact, 'privacy': page_privacy}
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

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    urls = []
    for pid, fn in PAGES.items():
        for lang in ('el', 'en'):
            u = url(pid, lang); write(u.lstrip('/') + 'index.html', fn(lang)); urls.append((pid, lang, u))
    for old, to in LEGACY.items(): write(f'{old}/index.html', redirect_page(to))
    write('404.html', page_404())
    if not PREFIX: write('CNAME', 'farazisgiannis.com\n')
    write('.nojekyll', '')
    # Search Console ownership file (URL-prefix property https://farazisgiannis.com/); keep it, or verification is lost
    write('google80208fabf8b37052.html', 'google-site-verification: google80208fabf8b37052.html')
    # Bing Webmaster Tools ownership file (same reason)
    write('BingSiteAuth.xml', '<?xml version="1.0"?>\n<users>\n\t<user>4DD6662B87831D9B870845ABE00172F7</user>\n</users>\n')
    # the preview must not be indexed (it would compete with the real address)
    write('robots.txt', 'User-agent: *\nDisallow: /\n' if PREFIX else f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for pid, lang, u in urls:
        sm.append(f'<url><loc>{BASE}{u}</loc><lastmod>{ASSET_V}</lastmod>'
                  f'<xhtml:link rel="alternate" hreflang="el" href="{BASE}{url(pid, "el")}"/><xhtml:link rel="alternate" hreflang="en" href="{BASE}{url(pid, "en")}"/></url>')
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
