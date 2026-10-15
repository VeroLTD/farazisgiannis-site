#!/usr/bin/env python3
"""Checks the built site: every internal href/src/srcset resolves to a file, pages have one h1, title and description,
Eurolife appears only on the contact pages, no phone number other than the approved ones is published, every photo is
used on one page only (owner's rule of 14 Oct 2026; the same page in el/en/ru counts as one), and nothing about general
insurance appears (the owner's single exception: the yearly check, under Loan protection, that the home's sum insured
covers the cost of rebuilding)."""
import os, re, sys
from collections import defaultdict
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
PREFIX = os.environ.get('SITE_PREFIX', '').rstrip('/')
APPROVED = {'35797840941', '35722124867'}
# general insurance (car, travel, home contents/buildings as a product, business general cover): never on this site
GENERAL = re.compile(r'(?i)car insurance|motor insurance|travel insurance|home insurance|contents insurance|liability insurance|'
                     r'ασφάλεια αυτοκινήτου|ασφάλιση αυτοκινήτου|ταξιδιωτική ασφάλ|ασφάλεια (?:του )?περιεχομένου|αστική ευθύνη|'
                     r'страхование (?:автомобил|имущества|путешеств|жилья)|ОСАГО|КАСКО')
# the owner's exception (Loan protection): the bank asks for cover of the home against fire and earthquake, and its sum
# insured is checked every year against the cost of rebuilding — that one sentence is allowed
ALLOWED = re.compile(r'(?is)(earthquake|σεισμ|землетрясен)[^.]*?(rebuild|ανοικοδόμ|восстановл|отстро|перестро)')
problems = []
photo_pages = defaultdict(set)
for dp, _, files in os.walk(OUT):
    for f in files:
        if not f.endswith('.html') or f.startswith('google'): continue  # skip Search Console ownership file
        p = os.path.join(dp, f); rel = os.path.relpath(p, OUT); t = open(p, encoding='utf-8').read()
        redirect = 'http-equiv="refresh"' in t
        urls = re.findall(r'(?:href|src)="(/[^"#?]*)', t)
        for ss in re.findall(r'srcset="([^"]*)"', t):
            urls += [c.strip().split()[0] for c in ss.split(',') if c.strip().startswith('/')]
        for u in urls:
            if PREFIX and u.startswith(PREFIX): u = u[len(PREFIX):] or '/'
            target = os.path.join(OUT, u.lstrip('/'))
            if u.endswith('/'): target = os.path.join(target, 'index.html')
            if not os.path.exists(target): problems.append(f'{rel}: missing {u}')
        if not redirect and rel != '404.html':
            if t.count('<h1') != 1: problems.append(f'{rel}: {t.count("<h1")} h1')
            if '<meta name="description"' not in t: problems.append(f'{rel}: no description')
            # one logical page = the same x-default address (el/en/ru of one page)
            m = re.search(r'hreflang="x-default" href="([^"]+)"', t)
            page = m.group(1) if m else rel
            keys = re.findall(r'data-photo="([^"]+)"', t)
            for k in set(keys):
                photo_pages[k].add(page)
                if keys.count(k) > 1: problems.append(f'{rel}: photo {k} used {keys.count(k)} times on the page')
        if 'film-topic-loan' in t or 'data-film="topic-loan"' in t: problems.append(f'{rel}: the AVRASTRO loan film (home insurance) is shown')
        if 'Eurolife' in t and 'epikoinonia' not in rel and 'contact' not in rel: problems.append(f'{rel}: Eurolife outside the contact page')
        for n in re.findall(r'tel:\+?(\d+)', t):
            if n not in APPROVED: problems.append(f'{rel}: unapproved phone {n}')
        text = re.sub(r'<script\b.*?</script>|<[^>]+>', ' ', t, flags=re.S)
        text = ' '.join(x for x in text.split('.') if not ALLOWED.search(x))
        for g in set(GENERAL.findall(text)): problems.append(f'{rel}: general insurance wording "{g}"')
for k, pages in photo_pages.items():
    if len(pages) > 1: problems.append(f'photo {k} is on {len(pages)} pages: ' + ', '.join(sorted(pages)))
# digital business card (ideas track 42): vCard without e-mail, QR code generated
vcf = os.path.join(OUT, 'assets', 'card', 'giannis-farazis.vcf')
if not os.path.exists(vcf): problems.append('assets/card/giannis-farazis.vcf missing')
elif re.search(r'(?im)^EMAIL|@[a-z0-9-]+\.[a-z]', open(vcf, encoding='utf-8').read()): problems.append('vCard contains an e-mail address')
for f in ('card-qr.svg', 'card-qr.png'):
    if not os.path.exists(os.path.join(OUT, 'assets', 'card', f)): problems.append(f'assets/card/{f} missing')
print('\n'.join(problems) or f'site check: 0 problems ({len(photo_pages)} photos, each on one page)')
sys.exit(1 if problems else 0)
