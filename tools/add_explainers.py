#!/usr/bin/env python3
"""Copies the narrated explainer films this site shows from the AVRASTRO repository's web export
(tools/video/publish.mjs → dist/video/web/videos.json + files) into assets/video/explainers/, and writes
explainers.json for build.py. Files that are no longer used are removed from this folder.

  python3 tools/add_explainers.py ../vero-os/dist/video/web
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'assets/video/explainers')
KEYS = ['meet-giannis', 'topic-life', 'topic-health', 'topic-income', 'topic-retirement', 'topic-savings', 'topic-education',
        'topic-business', 'topic-group', 'topic-expats']


def main(src):
    man = json.load(open(os.path.join(src, 'videos.json'), encoding='utf8'))
    os.makedirs(DEST, exist_ok=True)
    out, keep = {}, {'explainers.json'}
    for it in man['items']:
        if it['key'] not in KEYS:
            continue
        for k in ('video', 'poster', 'vtt'):
            if it.get(k):
                shutil.copy2(os.path.join(src, it[k]), os.path.join(DEST, it[k]))
                keep.add(it[k])
        out.setdefault(it['key'], {})[it['lang']] = {k: it[k] for k in ('video', 'poster', 'vtt', 'title', 'description', 'duration') if k in it}
    for f in os.listdir(DEST):
        if f not in keep:
            os.remove(os.path.join(DEST, f))
    json.dump(out, open(os.path.join(DEST, 'explainers.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    size = sum(os.path.getsize(os.path.join(DEST, f)) for f in os.listdir(DEST)) / 1048576
    print(f'{sum(len(v) for v in out.values())} films, {size:.1f} MB in assets/video/explainers')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'vero-os', 'dist', 'video', 'web'))
