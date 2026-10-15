#!/usr/bin/env python3
"""Build only the explicitly referenced public presentation assets (stdlib only)."""
import argparse
from datetime import date
import html
import json
import re
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
from urllib.parse import urlsplit

# Fixed publication policy: no directory discovery or implicit new decks.
DECKS = {
    'ai-voice-assistant': {
        'count': 30,
        'videos': {11: 'videos/OMA-PV.mp4', 13: 'videos/ヘイ、オーマあなたは何ですか.mp4'},
        'flags': {'span': True, 'loop': False, 'muted': False},
        'viewer': ('index.html', 'style.css', 'app.js',
                   'vendor/reveal/reveal.js', 'vendor/reveal/reveal.css',
                   'vendor/reveal/reset.css', 'vendor/reveal/LICENSE'),
        'overlays': True,
    },
    'omarchy-meetup3-opening': {
        'count': 7,
        'videos': {1: 'videos/omarchy-meetup.mp4'},
        'flags': {'span': True, 'loop': True, 'muted': True, 'autoplay': True},
        'viewer': ('index.html',),
        'overlays': False,
    },
}


def asset(root, path, folder, suffix):
    if not isinstance(path, str):
        raise ValueError('Asset paths must be strings')
    parts = PurePosixPath(path).parts
    if len(parts) != 2 or parts[0] != folder or any(c in path for c in '\\:%?#') or parts[1] in ('.', '..') or not path.endswith(suffix):
        raise ValueError(f'Unsafe asset path: {path!r}')
    candidate = root / path
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Asset escapes source directory: {path!r}')
    if not candidate.is_file():
        raise ValueError(f'Missing asset: {path!r}')
    return candidate


SOURCE_HOSTS = {'Speaker Deck': 'speakerdeck.com', 'SlideShare': 'www.slideshare.net'}
THUMBNAIL_HOSTS = {'Speaker Deck': 'files.speakerdeck.com', 'SlideShare': 'cdn.slidesharecdn.com'}
OPENING_URL = './omarchy-meetup3-opening/'


def https_url(value, host):
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value) or '\\' in value:
        raise ValueError('Unsafe catalog URL')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or parsed.netloc != host or not parsed.path.startswith('/'):
        raise ValueError(f'Unsafe catalog URL: {value!r}')


def site_file(site, name):
    path = site / name
    if not path.is_file() or not path.resolve().is_relative_to(site.resolve()):
        raise ValueError(f'Missing or unsafe site file: {name}')
    return path


def load_catalog(root):
    site = root / 'site'
    if not site.resolve().is_relative_to(root.resolve()):
        raise ValueError('Site directory escapes repository')
    catalog = json.loads(site_file(site, 'catalog.json').read_text(encoding='utf-8'))
    if not isinstance(catalog, dict) or set(catalog) != {'retrieved_at', 'presentations'}:
        raise ValueError('Malformed catalog')
    if not isinstance(catalog['retrieved_at'], str):
        raise ValueError('Missing catalog retrieval date')
    date.fromisoformat(catalog['retrieved_at'])
    if not isinstance(catalog['presentations'], list) or not catalog['presentations']:
        raise ValueError('Catalog must contain presentations')
    assets = {name: site_file(site, name) for name in ('catalog.css', 'catalog.js', 'catalog.json')}
    template = site_file(site, 'index.html').read_text(encoding='utf-8')
    if template.count('{{CARDS}}') != 1:
        raise ValueError('Template must contain one card placeholder')
    ids = set()
    cards = []
    for entry in catalog['presentations']:
        required = {'id', 'source', 'title', 'url', 'date', 'slides', 'thumbnail'}
        if not isinstance(entry, dict) or not required <= set(entry) or set(entry) - required - {'thumbnail_url'}:
            raise ValueError('Malformed catalog record')
        identifier = entry['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier) or identifier in ids:
            raise ValueError('Invalid or duplicate catalog ID')
        ids.add(identifier)
        source = entry['source']
        if source not in (*SOURCE_HOSTS, 'Local'):
            raise ValueError('Invalid catalog source')
        if not isinstance(entry['title'], str) or not entry['title'].strip():
            raise ValueError('Missing catalog title')
        if entry['date'] is not None:
            if not isinstance(entry['date'], str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', entry['date']):
                raise ValueError('Invalid catalog date')
            date.fromisoformat(entry['date'])
        if entry['slides'] is not None and (type(entry['slides']) is not int or entry['slides'] < 1):
            raise ValueError('Invalid slide count')
        if source in SOURCE_HOSTS:
            https_url(entry['url'], SOURCE_HOSTS[source])
            if 'thumbnail_url' in entry:
                https_url(entry['thumbnail_url'], THUMBNAIL_HOSTS[source])
        elif entry['url'] not in ('./ai-voice-assistant/', OPENING_URL):
            raise ValueError('Invalid local presentation link')
        if entry['thumbnail'] == './ai-voice-assistant/slides/slide-001.png' and source == 'Local':
            asset(root / 'ai-voice-assistant/web', 'slides/slide-001.png', 'slides', '.png')
        else:
            if not isinstance(entry['thumbnail'], str) or not re.fullmatch(r'\./images/[a-z0-9-]+\.jpg', entry['thumbnail']):
                raise ValueError('Unsafe catalog thumbnail')
            relative = entry['thumbnail'][2:]
            assets[relative] = asset(site, relative, 'images', '.jpg')
        escape = lambda value: html.escape(str(value), quote=True)
        source_label = 'このサイト' if source == 'Local' else source
        destination = 'スライドを見る' if source == 'Local' else f'{source} で見る'
        published = f'<time datetime="{escape(entry["date"])}">{escape(entry["date"].replace("-", "."))}</time>' if entry['date'] else '<span>日付不明</span>'
        slides = f'<span>{entry["slides"]} slides</span>' if entry['slides'] is not None else ''
        cards.append(f'''<article class="card" data-source="{escape(source)}" data-title="{escape(entry['title'])}" id="{escape(identifier)}">
<a class="card-link" href="{escape(entry['url'])}">
<div class="thumbnail"><img src="{escape(entry['thumbnail'])}" alt="" loading="lazy" width="640" height="360"></div>
<div class="card-body"><div class="metadata"><span class="source">{escape(source_label)}</span>{published}{slides}</div>
<h2>{escape(entry['title'])}</h2><span class="destination">{escape(destination)} <span aria-hidden="true">↗</span></span></div>
</a></article>''')
    page = template.replace('{{COUNT}}', str(len(cards))).replace('{{CARDS}}', '\n'.join(cards))
    return page, assets


def load_deck(root, name, spec):
    deck = root / name
    web = deck / 'web'
    if not deck.resolve().is_relative_to(root.resolve()) or deck.is_symlink() or web.is_symlink() or not web.resolve().is_relative_to(deck.resolve()):
        raise ValueError(f'Deck directory escapes source: {name}')
    manifest = web / 'slides.json'
    if not manifest.is_file() or not manifest.resolve().is_relative_to(web.resolve()):
        raise ValueError(f'Missing or unsafe manifest: {name}')
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'title', 'slides'} or not isinstance(data['title'], str) or not data['title'].strip() or not isinstance(data['slides'], list) or len(data['slides']) != spec['count']:
        raise ValueError(f"{name}: manifest must contain a title and exactly {spec['count']} slides")
    assets = {}
    for number, slide in enumerate(data['slides'], 1):
        allowed = {'image', 'description'}
        if number in spec['videos']:
            allowed |= {'video'} | set(spec['flags'])
            if spec['overlays']:
                allowed.add('overlay_image')
        if not isinstance(slide, dict) or set(slide) - allowed:
            raise ValueError(f'{name}: malformed slide {number}')
        if not isinstance(slide.get('description'), str) or not slide['description'].strip():
            raise ValueError(f'Missing description on slide {number}')
        if slide.get('image') != f'slides/slide-{number:03}.png':
            raise ValueError(f'Unsafe or out-of-order image on slide {number}')
        assets[slide['image']] = asset(web, slide['image'], 'slides', '.png')
        if number in spec['videos']:
            if slide.get('video') != spec['videos'][number]:
                raise ValueError(f'Unexpected video on slide {number}')
            for flag, expected in spec['flags'].items():
                if slide.get(flag) is not expected:
                    raise ValueError(f'Invalid {flag} on slide {number}')
            assets[slide['video']] = asset(deck, slide['video'], 'videos', '.mp4')
        if 'overlay_image' in slide:
            assets[slide['overlay_image']] = asset(web, slide['overlay_image'], 'slides', '.png')
    for relative in spec['viewer']:
        source = web / relative
        if not source.is_file() or not source.resolve().is_relative_to(web.resolve()):
            raise ValueError(f'Missing or unsafe viewer file: {relative}')
        assets[relative] = source
    return data, assets


def build(root, output):
    page, site_assets = load_catalog(root)
    assets = dict(site_assets)
    manifests = {}
    for name, spec in DECKS.items():
        data, deck_assets = load_deck(root, name, spec)
        manifests[f'{name}/slides.json'] = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        assets.update({f'{name}/{relative}': source for relative, source in deck_assets.items()})
    if sum(p.stat().st_size for p in assets.values()) >= 30_000_000:
        raise ValueError('Artifact exceeds 30 MB budget')
    if output.is_symlink():
        raise ValueError('Output must not be a symlink')
    output = output.resolve()
    # Never replace repository/source directories or a non-build directory.
    if root.resolve().is_relative_to(output) or any(output.is_relative_to((root / name).resolve()) for name in (*DECKS, 'site')):
        raise ValueError('Output overlaps source files')
    expected_files = {'index.html'} | set(assets) | set(manifests)
    expected_dirs = {parent.as_posix() for name in expected_files
                     for parent in PurePosixPath(name).parents if parent != PurePosixPath('.')}
    if output.exists():
        if not output.is_dir():
            raise ValueError('Output must be a directory')
        for path in output.rglob('*'):
            relative = path.relative_to(output).as_posix()
            if path.is_symlink() or relative not in (expected_dirs if path.is_dir() else expected_files):
                raise ValueError('Output contains unrelated files; choose an empty build directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pages-build-', dir=output.parent) as directory:
        stage = Path(directory)
        for relative, source in assets.items():
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        for relative, manifest in manifests.items():
            (stage / relative).write_text(manifest, encoding='utf-8')
        (stage / 'index.html').write_text(page, encoding='utf-8')
        if sum(p.stat().st_size for p in stage.rglob('*') if p.is_file()) >= 30_000_000:
            raise ValueError('Artifact exceeds 30 MB budget')
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage, output)
    files = [p for p in output.rglob('*') if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    if total >= 30_000_000:
        raise ValueError('Artifact exceeds 30 MB budget')
    print(f'Built {output}: {len(files)} files, {total} bytes')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--output', type=Path, default=Path('_site'))
    args = parser.parse_args()
    try:
        build(args.root.resolve(), args.output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
