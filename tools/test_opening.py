"""Opening deck content, two-deck packaging, and media policy regression tests."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

import test_build_pages

ROOT = test_build_pages.ROOT


class OpeningTest(unittest.TestCase):
    fixture = test_build_pages.PackagingTest.fixture
    run_build = test_build_pages.PackagingTest.run_build

    def test_opening_output_is_portable_and_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            output = root / '_site'
            result = self.run_build(root, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            target = output / 'omarchy-meetup3-opening'
            self.assertTrue((target / 'slides.json').exists(), 'Opening must be published')
            manifest = json.loads((target / 'slides.json').read_text())
            self.assertEqual(len(manifest['slides']), 7)
            self.assertEqual(manifest['slides'][0], {
                'image': 'slides/slide-001.png', 'description': 'Opening slide 1',
                'video': 'videos/omarchy-meetup.mp4', 'span': True, 'loop': True,
                'muted': True, 'autoplay': True,
            })
            self.assertEqual({p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()},
                             {'index.html', 'slides.json', 'videos/omarchy-meetup.mp4'} |
                             {f'slides/slide-{i:03}.png' for i in range(1, 8)})
            before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
            self.assertEqual(self.run_build(root, output).returncode, 0)
            self.assertEqual(before, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_invalid_opening_never_replaces_previous_output(self):
        cases = ['count', 'image', 'video', 'overlay', 'static-flags', 'static-autoplay', 'missing-image',
                 'missing-video', 'escaping-image', 'escaping-manifest', 'escaping-deck', 'escaping-web']
        cases += [f'flag-{flag}' for flag in ('span', 'loop', 'muted', 'autoplay')]
        for kind in cases:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                web = root / 'omarchy-meetup3-opening/web'
                output = root / '_site'
                self.assertEqual(self.run_build(root, output).returncode, 0)
                before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
                path = web / 'slides.json'
                manifest = json.loads(path.read_text())
                if kind == 'count':
                    manifest['slides'].pop()
                elif kind == 'image':
                    manifest['slides'][1]['image'] = '../private.png'
                elif kind == 'video':
                    manifest['slides'][0]['video'] = 'videos/unapproved.mp4'
                elif kind == 'overlay':
                    manifest['slides'][0]['overlay_image'] = 'slides/overlay-1.png'
                elif kind.startswith('static-'):
                    manifest['slides'][1]['autoplay' if kind == 'static-autoplay' else 'loop'] = True
                elif kind.startswith('flag-'):
                    manifest['slides'][0][kind[5:]] = False
                elif kind in ('missing-image', 'missing-video', 'escaping-image'):
                    source = web / 'slides/slide-002.png' if kind != 'missing-video' else root / 'omarchy-meetup3-opening/videos/omarchy-meetup.mp4'
                    source.unlink()
                    if kind == 'escaping-image':
                        source.symlink_to(root / 'site/images/example.jpg')
                elif kind == 'escaping-manifest':
                    private = root / 'private.json'
                    private.write_text(path.read_text())
                    path.unlink()
                    path.symlink_to(private)
                else:
                    source = web if kind == 'escaping-web' else web.parent
                    private = root / 'private-deck'
                    source.rename(private)
                    source.symlink_to(private, target_is_directory=True)
                if kind != 'escaping-manifest':
                    path.write_text(json.dumps(manifest))
                result = self.run_build(root, output)
                self.assertNotEqual(result.returncode, 0, kind)
                self.assertEqual(before, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_ai_autoplay_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            web, manifest = self.fixture(root)
            manifest['slides'][10]['autoplay'] = True
            (web / 'slides.json').write_text(json.dumps(manifest))
            self.assertNotEqual(self.run_build(root, root / '_site').returncode, 0)

    def test_committed_opening_assets_and_shared_viewer_contract(self):
        web = ROOT / 'omarchy-meetup3-opening/web'
        self.assertTrue((web / 'slides.json').is_file(), 'Portable Opening manifest must exist')
        data = json.loads((web / 'slides.json').read_text())
        self.assertEqual(data['title'], 'Omarchy Meetup Tokyo Night — Opening')
        self.assertEqual(len(data['slides']), 7)
        for number, slide in enumerate(data['slides'], 1):
            self.assertEqual(slide['image'], f'slides/slide-{number:03}.png')
            self.assertTrue(slide['description'].strip())
            content = (web / slide['image']).read_bytes()
            self.assertEqual(content[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II', content[16:24]), (1920, 1080))
        self.assertNotIn('/tmp/', json.dumps(data))
        self.assertNotIn('overlay_image', json.dumps(data))
        page = (web / 'index.html').read_text()
        self.assertIn('data-slide-count="7"', page)
        for resource in ('app.js', 'style.css', 'vendor/reveal/reveal.js', 'vendor/reveal/reveal.css', 'vendor/reveal/reset.css'):
            self.assertIn(f'../ai-voice-assistant/{resource}', page)
if __name__ == '__main__':
    unittest.main()
