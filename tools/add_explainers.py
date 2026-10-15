#!/usr/bin/env python3
"""Copies the narrated explainer films this site shows from the AVRASTRO repository's web export
(tools/video/publish.mjs → dist/video/web/videos.json + files) into assets/video/explainers/, and writes
explainers.json for build.py. Every film in Greek, English and Russian (when the export has them). Files that are no
longer used are removed from this folder.

  python3 tools/add_explainers.py ../vero-os/dist/video/web

Which films: KEYS below — the films whose `places` in vero-os tools/video/scripts.mjs name farazisgiannis.com
(`node tools/video/scripts.mjs --list`). topic-loan is NOT one of them: it also covers cover for the home against fire,
earthquake and flood, so Loan protection shows fg-loan (life only).

Posters (owner's rule of 14 Oct 2026: no picture twice on the site): with ffmpeg on the PATH, extra poster frames are
taken from the film itself — meet-giannis gets one near its end (its first frame is the portrait, which the About page
already shows), fg-cities gets one per city page (the same film is on five pages). Without ffmpeg the film's own poster
is used.
"""
import json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'assets/video/explainers')
KEYS = ['meet-giannis',
        'topic-life', 'topic-health', 'topic-income', 'topic-retirement', 'topic-savings', 'topic-education',
        'topic-business', 'topic-group', 'topic-expats', 'topic-review',
        'fg-how', 'fg-first-meeting', 'fg-callback', 'fg-employers', 'fg-checklist-claims', 'fg-checklist-signing',
        'fg-yearly-check', 'fg-loan', 'fg-savings', 'fg-cities']
EXCLUDED = {'topic-loan'}   # never on farazisgiannis.com (general insurance in the film)
LANGS = ('el', 'en', 'ru')
CITY_KEYS = ['nicosia', 'limassol', 'larnaca', 'paphos', 'famagusta']   # build.py CITIES order
ALT_AT = {'meet-giannis': [('alt', .96)], 'fg-cities': [(c, .18 + i * .15) for i, c in enumerate(CITY_KEYS)]}


def frame(video, at, out):
    """one frame of the film at `at` seconds as a JPEG poster; False if ffmpeg is not there or fails"""
    if not shutil.which('ffmpeg'):
        return False
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f'{at:.2f}', '-i', video, '-frames:v', '1', '-q:v', '3', out])
    return r.returncode == 0 and os.path.exists(out)


def main(src):
    man = json.load(open(os.path.join(src, 'videos.json'), encoding='utf8'))
    os.makedirs(DEST, exist_ok=True)
    out, keep = {}, {'explainers.json'}
    for it in man['items']:
        if it['key'] not in KEYS or it['key'] in EXCLUDED or it.get('lang') not in LANGS:
            continue
        for k in ('video', 'poster', 'vtt'):
            if it.get(k):
                shutil.copy2(os.path.join(src, it[k]), os.path.join(DEST, it[k]))
                keep.add(it[k])
        e = {k: it[k] for k in ('video', 'poster', 'vtt', 'title', 'description', 'duration', 'date') if k in it}
        for name, share in ALT_AT.get(it['key'], []):
            f = os.path.splitext(it['video'])[0] + f'-poster-{name}.jpg'
            if frame(os.path.join(DEST, it['video']), share * float(it.get('duration') or 0), os.path.join(DEST, f)):
                e.setdefault('posters', {})[name] = f; keep.add(f)
        out.setdefault(it['key'], {})[it['lang']] = e
    for f in os.listdir(DEST):
        if f not in keep:
            os.remove(os.path.join(DEST, f))
    json.dump(out, open(os.path.join(DEST, 'explainers.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    size = sum(os.path.getsize(os.path.join(DEST, f)) for f in os.listdir(DEST)) / 1048576
    missing = [f'{k}/{l}' for k in KEYS for l in LANGS if l not in out.get(k, {})]
    print(f'{sum(len(v) for v in out.values())} films, {size:.1f} MB in assets/video/explainers'
          + (f'; not in the export: {", ".join(missing)}' if missing else ''))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'vero-os', 'dist', 'video', 'web'))
