#!/usr/bin/env python3
"""Russian edition helper: lists every English text segment of the built English pages (site/en/**), so that
i18n/ru.json can map each one to Russian. Usage: python3 tools/ru_segments.py [--missing]  (after python3 build.py)."""
import json, os, re, sys
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTRS = ('alt', 'aria-label', 'title', 'placeholder', 'data-pause', 'data-play')
META = ('description', 'og:title', 'og:description')

def norm(t): return re.sub(r'\s+', ' ', t).strip()

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'script' and a.get('type') == 'application/ld+json': self.skip -= 1; self.ld = True
        for k in ATTRS:
            if a.get(k): self.out.append(norm(a[k]))
        if tag == 'meta' and (a.get('name') in META or a.get('property') in META) and a.get('content'): self.out.append(norm(a['content']))
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip: self.skip -= 1
        self.ld = False
    def handle_data(self, d):
        if getattr(self, 'ld', False):
            try: walk(json.loads(d), self.out)
            except Exception: pass
            return
        if self.skip: return
        t = norm(d)
        if t and re.search(r'[A-Za-z]', t): self.out.append(t)

def walk(j, out):
    if isinstance(j, dict):
        for k, v in j.items():
            if k in ('name', 'text', 'description', 'jobTitle') and isinstance(v, str): out.append(norm(v))
            else: walk(v, out)
    elif isinstance(j, list):
        for v in j: walk(v, out)

def segments():
    seen = []
    for dp, _, fs in os.walk(os.path.join(ROOT, 'site', 'en')):
        for f in sorted(fs):
            if f.endswith('.html'):
                p = P(); p.feed(open(os.path.join(dp, f), encoding='utf-8').read())
                for s in p.out:
                    if s not in seen: seen.append(s)
    return seen

if __name__ == '__main__':
    segs = segments()
    ru = json.load(open(os.path.join(ROOT, 'i18n', 'ru.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'i18n', 'ru.json')) else {}
    if '--missing' in sys.argv: segs = [s for s in segs if s not in ru]
    json.dump(segs, sys.stdout, ensure_ascii=False, indent=0); print(); print(len(segs), 'segments', file=sys.stderr)
