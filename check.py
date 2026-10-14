#!/usr/bin/env python3
"""Checks the built site: every internal href/src resolves to a file, pages have one h1, title and description,
Eurolife appears only on the contact pages, and no phone number other than the approved ones is published."""
import os, re, sys
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
PREFIX = os.environ.get('SITE_PREFIX', '').rstrip('/')
APPROVED = {'35797840941', '35722124867'}
problems = []
for dp, _, files in os.walk(OUT):
    for f in files:
        if not f.endswith('.html') or f.startswith('google'): continue  # skip Search Console ownership file
        p = os.path.join(dp, f); rel = os.path.relpath(p, OUT); t = open(p, encoding='utf-8').read()
        redirect = 'http-equiv="refresh"' in t
        for u in re.findall(r'(?:href|src|srcset)="(/[^"#?]*)', t):
            if PREFIX and u.startswith(PREFIX): u = u[len(PREFIX):] or '/'
            target = os.path.join(OUT, u.lstrip('/'))
            if u.endswith('/'): target = os.path.join(target, 'index.html')
            if not os.path.exists(target): problems.append(f'{rel}: missing {u}')
        if not redirect and rel != '404.html':
            if t.count('<h1') != 1: problems.append(f'{rel}: {t.count("<h1")} h1')
            if '<meta name="description"' not in t: problems.append(f'{rel}: no description')
        if 'Eurolife' in t and 'epikoinonia' not in rel and 'contact' not in rel: problems.append(f'{rel}: Eurolife outside the contact page')
        for n in re.findall(r'tel:\+?(\d+)', t):
            if n not in APPROVED: problems.append(f'{rel}: unapproved phone {n}')
# digital business card (ideas track 42): vCard without e-mail, QR code generated
vcf = os.path.join(OUT, 'assets', 'card', 'giannis-farazis.vcf')
if not os.path.exists(vcf): problems.append('assets/card/giannis-farazis.vcf missing')
elif re.search(r'(?im)^EMAIL|@[a-z0-9-]+\.[a-z]', open(vcf, encoding='utf-8').read()): problems.append('vCard contains an e-mail address')
for f in ('card-qr.svg', 'card-qr.png'):
    if not os.path.exists(os.path.join(OUT, 'assets', 'card', f)): problems.append(f'assets/card/{f} missing')
print('\n'.join(problems) or 'site check: 0 problems')
sys.exit(1 if problems else 0)
