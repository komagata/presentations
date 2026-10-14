#!/usr/bin/env python3
"""Build only the explicitly referenced public presentation assets (stdlib only)."""
import argparse
import html
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile

VIDEOS = {10: 'videos/ヘイ、オーマあなたは何ですか.mp4', 12: 'videos/OMA-PV.mp4'}


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


def build(root, output):
    deck = root / 'ai-voice-assistant'
    web = deck / 'web'
    data = json.loads((web / 'slides.json').read_text())
    if not isinstance(data, dict) or set(data) != {'title', 'slides'} or not isinstance(data['title'], str) or not isinstance(data['slides'], list) or len(data['slides']) != 30:
        raise ValueError('Manifest must contain a title and exactly 30 slides')
    assets = {}
    for number, slide in enumerate(data['slides'], 1):
        if not isinstance(slide, dict) or set(slide) - {'image', 'description', 'video', 'overlay_image', 'span', 'loop', 'muted'}:
            raise ValueError(f'Malformed slide {number}')
        if not isinstance(slide.get('description'), str) or not slide['description'].strip():
            raise ValueError(f'Missing description on slide {number}')
        if slide.get('image') != f'slides/slide-{number:03}.png':
            raise ValueError(f'Unsafe or out-of-order image on slide {number}')
        assets[slide['image']] = asset(web, slide['image'], 'slides', '.png')
        if number in VIDEOS:
            if slide.get('video') != VIDEOS[number] or slide.get('muted') is not False:
                raise ValueError(f'Expected audible video on slide {number}')
            for flag in ('span', 'loop', 'muted'):
                if type(slide.get(flag)) is not bool:
                    raise ValueError(f'Invalid {flag} on slide {number}')
            assets[slide['video']] = asset(deck, slide['video'], 'videos', '.mp4')
        elif 'video' in slide:
            raise ValueError(f'Unexpected video on slide {number}')
        if 'overlay_image' in slide:
            if number not in VIDEOS:
                raise ValueError(f'Unexpected overlay on slide {number}')
            assets[slide['overlay_image']] = asset(web, slide['overlay_image'], 'slides', '.png')
    for name in ('index.html', 'style.css', 'app.js'):
        assets[name] = web / name
        if not assets[name].is_file() or not assets[name].resolve().is_relative_to(web.resolve()):
            raise ValueError(f'Missing or unsafe viewer file: {name}')
    if sum(p.stat().st_size for p in assets.values()) >= 30_000_000:
        raise ValueError('Artifact exceeds 30 MB budget')
    if output.is_symlink():
        raise ValueError('Output must not be a symlink')
    output = output.resolve()
    # Never replace repository/source directories or a non-build directory.
    if root.resolve().is_relative_to(output) or output.is_relative_to(web.resolve()) or output.is_relative_to((deck / 'videos').resolve()):
        raise ValueError('Output overlaps source files')
    expected_files = {'index.html', 'ai-voice-assistant/slides.json'} | {f'ai-voice-assistant/{name}' for name in assets}
    expected_dirs = {'ai-voice-assistant', 'ai-voice-assistant/slides', 'ai-voice-assistant/videos'}
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
        target = stage / 'ai-voice-assistant'
        target.mkdir()
        for relative, source in assets.items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        (target / 'slides.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        title = html.escape(data['title'])
        (stage / 'index.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Presentations · komagata</title>
<style>body{{background:#1a1b26;color:#c0caf5;font:1.1rem system-ui;max-width:48rem;margin:12vh auto;padding:1.5rem}}a{{color:#7aa2f7}}a:focus-visible{{outline:3px solid #e0af68;outline-offset:5px}}</style>
<h1>Presentations</h1><p><a href="./ai-voice-assistant/">{title}</a> — 30 slides with two videos.</p></html>\n''')
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
