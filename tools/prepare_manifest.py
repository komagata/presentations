#!/usr/bin/env python3
"""Convert a local Hype render manifest into the public viewer manifest."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / 'ai-voice-assistant'
WEB = DECK / 'web'


def main():
    renderer = WEB / 'slides/slides.json'
    data = json.loads(renderer.read_text())
    markdown = (DECK / 'AI Voice Assistant.md').read_text()
    markdown = re.sub(r'\A---\n.*?\n---\n', '', markdown, count=1, flags=re.S)
    pages = re.split(r'^---\s*$', markdown, flags=re.M)
    if len(pages) != 30 or len(data['slides']) != 30:
        raise ValueError('Expected exactly 30 rendered slides and Markdown pages')
    image_descriptions = {
        3: 'Grok bot, dots, and OpenClaw mascots.',
        6: 'HAL 9000, a red camera eye.',
        7: 'MU/TH/UR computer from Alien.',
        8: 'TARS robot from Interstellar.',
        17: 'Diagram: OMA provides a GUI and voice interface layer for AI agents.',
        20: 'Diagram: Listen with GPT Live, Speak with GPT Live, Think with Codex.',
        22: 'Diagram: Listen with Whisper, Speak with Qwen3, Think with Claude.',
        25: 'Annotated OMA user interface.',
    }
    video_descriptions = {11: 'Video: OMA promotional demonstration.', 13: 'Video: asking OMA what it is (Japanese).'}
    slides = []
    for number, (source, page) in enumerate(zip(data['slides'], pages), 1):
        text = re.sub(r'<!--.*?-->', '', page, flags=re.S)
        text = re.sub(r'!\[[^\]]*\]\([^\n]*\)', '', text)
        text = re.sub(r'^\s*[#-]+\s*', '', text, flags=re.M)
        text = ' '.join(text.split())
        description = ' '.join(part for part in (text, image_descriptions.get(number), video_descriptions.get(number)) if part)
        slide = {'image': f"slides/{Path(source['image']).name}", 'description': description}
        if 'video' in source:
            name = Path(source['video']).name
            expected = {11: 'OMA-PV.mp4', 13: 'ヘイ、オーマあなたは何ですか.mp4'}.get(number)
            if name != expected:
                raise ValueError(f'Unexpected video on slide {number}')
            slide.update(video=f'videos/{name}', span=bool(source.get('span', False)), loop=bool(source.get('loop', False)), muted=False)
            if source.get('overlay_image'):
                slide['overlay_image'] = f"slides/{Path(source['overlay_image']).name}"
        slides.append(slide)
    public = {'title': data['title'], 'slides': slides}
    encoded = json.dumps(public, ensure_ascii=False, indent=2) + '\n'
    (WEB / 'slides.json').write_text(encoded)
    # Retain the renderer manifest as portable metadata; the viewer uses ../slides.json.
    renderer.write_text(encoded)
    print('Wrote portable web/slides.json and web/slides/slides.json')


if __name__ == '__main__':
    main()
