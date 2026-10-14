#!/usr/bin/env python3
"""Downloads the photos the site still needs — runs on GitHub's machines (workflow «Site photos»,
.github/workflows/photos.yml); the build sandbox has no internet access.

For every slot in tools/photos/manifest.json with a "fetch" block and no download yet (tools/photos/fetched/fetched.json):
  1. search, in order: Pixabay (Pixabay Content License; only when the secret PIXABAY_API_KEY is set) and Openverse
     (CC0 1.0 / Public Domain Mark only). Nothing under any other licence is ever downloaded.
  2. take the first landscape result, at least 1280 px wide, that is not already on the site (same provider id, or the
     same picture by fingerprint: tools/photos/audit.py) — or the candidate named in "pick" ("pixabay-123", "ov-<uuid>").
  3. save it as tools/photos/fetched/<slot>.jpg (max 2400 px wide), its credit in fetched.json, the next candidates in
     fetched/candidates/<slot>.json, and a contact sheet fetched/sheet.jpg to look at before approving.
The workflow then runs make_variants.py and audit.py and commits the result to the same branch, where build.py uses it.
To change a choice: put "pick": "<provider>-<id>" (from candidates/<slot>.json) in the slot, delete its entry from
fetched.json, push. Env: PHOTO_SLOTS=a,b limits the run; PHOTO_REFETCH=a,b downloads those slots again.
"""
import io, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit  # noqa: E402

FETCHED = os.path.join(HERE, 'fetched')
UA = 'farazisgiannis-site-photos/1.0 (+https://farazisgiannis.com; site imagery)'
PIXABAY = os.environ.get('PIXABAY_API_KEY', '').strip()
ONLY = set(filter(None, os.environ.get('PHOTO_SLOTS', '').split(',')))
REFETCH = set(filter(None, os.environ.get('PHOTO_REFETCH', '').split(',')))
MIN_W = 1280

def get(url, headers=None, limit=30_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read(limit + 1)
    if len(data) > limit: raise ValueError('too large')
    return data

def pixabay(q):
    if not PIXABAY: return []
    u = 'https://pixabay.com/api/?' + urllib.parse.urlencode({'key': PIXABAY, 'q': q, 'image_type': 'photo', 'orientation': 'horizontal',
                                                             'safesearch': 'true', 'per_page': 20, 'min_width': MIN_W, 'order': 'popular'})
    js = json.loads(get(u))
    return [{'provider': 'pixabay', 'id': str(h['id']), 'page': h['pageURL'], 'creator': h.get('user'), 'title': h.get('tags', ''),
             'license': 'Pixabay Content License', 'license_url': 'https://pixabay.com/service/license-summary/',
             'width': h.get('imageWidth'), 'download': h.get('largeImageURL'), 'preview': h.get('webformatURL')} for h in js.get('hits', [])]

_last = [0.0]
def openverse(q):
    wait = 12 - (time.time() - _last[0])   # the anonymous API allows a few requests a minute
    if wait > 0: time.sleep(wait)
    _last[0] = time.time()
    u = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode({'q': q, 'license': 'cc0,pdm', 'category': 'photograph', 'aspect_ratio': 'wide',
                                                                           'size': 'large', 'mature': 'false', 'page_size': 20})
    try:
        js = json.loads(get(u, {'Accept': 'application/json'}))
    except urllib.error.HTTPError as e:
        print(f'::warning title=photos::Openverse refused "{q}" (HTTP {e.code})'); return []
    out = []
    for r in js.get('results', []):
        lic = (r.get('license') or '').lower()
        if lic not in ('cc0', 'pdm'): continue
        out.append({'provider': 'ov', 'id': r['id'], 'page': r.get('foreign_landing_url') or r.get('url'), 'creator': r.get('creator'), 'title': r.get('title') or '',
                    'license': 'CC0 1.0' if lic == 'cc0' else 'Public Domain Mark 1.0',
                    'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/' if lic == 'cc0' else 'https://creativecommons.org/publicdomain/mark/1.0/',
                    'width': r.get('width'), 'download': r.get('url'), 'preview': r.get('thumbnail') or r.get('url')})
    return out

def main():
    man = json.load(open(os.path.join(HERE, 'manifest.json'), encoding='utf-8'))
    os.makedirs(os.path.join(FETCHED, 'candidates'), exist_ok=True)
    fpath = os.path.join(FETCHED, 'fetched.json')
    done = json.load(open(fpath, encoding='utf-8')) if os.path.exists(fpath) else {}
    used_ids = {(v['provider'], v['id']) for v in done.values()}
    used_ids |= {('ov', s['credit']['openverse_id']) for s in man['slots'].values() if s.get('credit', {}).get('openverse_id')}
    known = dict(man.get('reserved', {}))
    for f in os.listdir(os.path.join(HERE, '..', '..', 'assets', 'img', 'photos')):
        if f.endswith('-480.webp'): known['site:' + f] = audit.dhash(os.path.join(HERE, '..', '..', 'assets', 'img', 'photos', f))
    for k in done:
        p = os.path.join(FETCHED, k + '.jpg')
        if os.path.exists(p): known['fetched:' + k] = audit.dhash(p)
    report = []
    for key, slot in man['slots'].items():
        fx = slot.get('fetch')
        if not fx or (ONLY and key not in ONLY) or (key in done and key not in REFETCH): continue
        cands = []
        for q in fx['queries']:
            for prov in (pixabay, openverse):
                try: cands += prov(q)
                except Exception as e: print(f'::warning title=photos::{key}: {prov.__name__} "{q}": {e}')
        seen, uniq = set(), []
        for c in cands:
            if (c['provider'], c['id']) in seen or (c['provider'], c['id']) in used_ids: continue
            if c.get('width') and c['width'] < MIN_W: continue
            seen.add((c['provider'], c['id'])); uniq.append(c)
        pick = fx.get('pick')
        if pick: uniq.sort(key=lambda c: f"{c['provider']}-{c['id']}" != pick)
        with open(os.path.join(FETCHED, 'candidates', key + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(uniq[:12], fh, ensure_ascii=False, indent=1)
        chosen = None
        for c in uniq[:12]:
            try:
                im = ImageOps.exif_transpose(Image.open(io.BytesIO(get(c['download'])))).convert('RGB')
            except Exception as e:
                print(f'::warning title=photos::{key}: {c["provider"]}-{c["id"]} could not be downloaded: {e}'); continue
            if im.width < MIN_W or im.width / im.height < 1.3: continue
            if im.width > 2400: im = im.resize((2400, round(im.height * 2400 / im.width)), Image.LANCZOS)
            tmp = os.path.join(FETCHED, key + '.jpg')
            im.save(tmp, 'JPEG', quality=88, optimize=True, progressive=True)
            h = audit.dhash(tmp)
            twin = next((n for n, kh in known.items() if audit.dist(h, kh) <= audit.LIMIT), None)
            if twin:
                print(f'{key}: {c["provider"]}-{c["id"]} is the same picture as {twin}; next'); os.remove(tmp); continue
            chosen = c; known['fetched:' + key] = h; break
        if not chosen:
            report.append(f'{key}: nothing suitable found'); continue
        chosen = {k: v for k, v in chosen.items() if k not in ('download', 'preview')}
        chosen['fetched'] = time.strftime('%Y-%m-%d'); chosen['review'] = 'pending: look at fetched/sheet.jpg'
        done[key] = chosen; used_ids.add((chosen['provider'], chosen['id']))
        report.append(f'{key}: {chosen["provider"]}-{chosen["id"]} ({chosen["license"]}) {chosen["page"]}')
    with open(fpath, 'w', encoding='utf-8') as fh:
        json.dump(done, fh, ensure_ascii=False, indent=1); fh.write('\n')
    # contact sheet of every downloaded photo, to look at before the preview is approved
    files = [(k, os.path.join(FETCHED, k + '.jpg')) for k in done if os.path.exists(os.path.join(FETCHED, k + '.jpg'))]
    if files:
        W, H = 480, 320
        sheet = Image.new('RGB', (W * 2, (H + 24) * ((len(files) + 1) // 2)), 'white'); d = ImageDraw.Draw(sheet)
        for i, (k, f) in enumerate(files):
            im = Image.open(f); im.thumbnail((W, H)); x, y = (i % 2) * W, (i // 2) * (H + 24)
            sheet.paste(im, (x, y)); d.text((x + 4, y + H + 5), f'{k}: {done[k]["provider"]}-{done[k]["id"]}', fill='black')
        sheet.save(os.path.join(FETCHED, 'sheet.jpg'), quality=80)
    print('\n'.join(report) or 'nothing to fetch')
    if report and os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as fh:
            fh.write('### Site photos\n\n' + '\n'.join('- ' + r for r in report) + '\n')

if __name__ == '__main__':
    main()
