"""Regression tests for the actual static publication boundary."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('build_pages.py')
ROOT = SCRIPT.parent.parent


class PackagingTest(unittest.TestCase):
    def fixture(self, root):
        web = root / 'ai-voice-assistant/web'
        (web / 'slides').mkdir(parents=True)
        videos = root / 'ai-voice-assistant/videos'
        videos.mkdir()
        for name in ('index.html', 'style.css', 'app.js'):
            (web / name).write_text('fixture')
        vendor = web / 'vendor/reveal'
        vendor.mkdir(parents=True)
        for name in ('reveal.js', 'reveal.css', 'reset.css', 'LICENSE'):
            (vendor / name).write_text(f'pinned {name}')
        (vendor / 'private.txt').write_text('must not publish')
        (vendor / 'README.md').write_text('must not publish')
        slides = []
        for number in range(1, 31):
            path = f'slides/slide-{number:03}.png'
            (web / path).write_bytes(b'png')
            slide = {'image': path, 'description': f'Slide {number}'}
            if number in (11, 13):
                name = 'OMA-PV.mp4' if number == 11 else 'ヘイ、オーマあなたは何ですか.mp4'
                (videos / name).write_bytes(b'mp4')
                slide.update(video=f'videos/{name}', span=True, loop=False, muted=False)
            slides.append(slide)
        manifest = {'title': 'AI Voice Assistant', 'slides': slides}
        (web / 'slides.json').write_text(json.dumps(manifest))
        for path in ('export.pdf', 'validation.html', 'README.md'):
            (web / path).write_text('must not publish')
        (videos / 'unused.mp4').write_bytes(b'unused')
        opening = root / 'omarchy-meetup3-opening'
        opening_web = opening / 'web'
        (opening_web / 'slides').mkdir(parents=True)
        (opening_web / 'index.html').write_text('opening fixture')
        (opening / 'videos').mkdir()
        (opening / 'videos/omarchy-meetup.mp4').write_bytes(b'opening mp4')
        opening_slides = []
        for number in range(1, 8):
            path = f'slides/slide-{number:03}.png'
            (opening_web / path).write_bytes(b'opening png')
            slide = {'image': path, 'description': f'Opening slide {number}'}
            if number == 1:
                slide.update(video='videos/omarchy-meetup.mp4', span=True, loop=True, muted=True, autoplay=True)
            opening_slides.append(slide)
        (opening_web / 'slides.json').write_text(json.dumps({'title': 'Opening', 'slides': opening_slides}))
        (opening_web / 'slides/overlay-1.png').write_bytes(b'unused overlay')
        (opening_web / 'slides/slides.json').write_text('unpublished renderer metadata')
        marp = root / 'omarchy-for-ai-era'
        (marp / 'images/quattro-4.5').mkdir(parents=True)
        (marp / 'images/hardware').mkdir()
        (marp / 'omarchy-for-ai-era.html').write_text(
            '<style>div#\\:\\$p {} .bg { background-image: url("data:image/png;base64,YQ==") }</style>'
            '<img src="images/icon.png"><img src="data:image/png;base64,YQ==">'
            '<div style="background-image:url(&quot;images/quattro-4.5/../hardware/bg.webp&quot;)"></div>'
            '<video src="images/demo.mp4" poster="images/poster.jpg"></video>'
            '<a href="https://example.com">link</a>')
        for name in ('icon.png', 'hardware/bg.webp', 'demo.mp4', 'poster.jpg'):
            (marp / 'images' / name).write_bytes(name.encode())
        for name in ('draft.md', 'export.pptx', 'backup.html', 'sources.json'):
            (marp / name).write_text('must not publish')
        (marp / 'images/unused.png').write_bytes(b'unused')
        apps = root / 'ore-no-omarchy-apps'
        (apps / 'images').mkdir(parents=True)
        (apps / 'ore-no-omarchy-apps.html').write_text('<img src="images/app.webp">')
        (apps / 'images/app.webp').write_bytes(b'app image')
        (apps / 'images/unused.png').write_bytes(b'unused')
        (apps / 'draft.md').write_text('must not publish')
        site = root / 'site'
        (site / 'images').mkdir(parents=True)
        for name in ('index.html', 'catalog.css', 'catalog.js'):
            (site / name).write_text('<main>{{CARDS}}</main>' if name == 'index.html' else 'fixture')
        (site / 'images/example.jpg').write_bytes(b'jpg')
        catalog = {'retrieved_at': '2026-10-15', 'presentations': [{
            'id': 'speakerdeck-example', 'source': 'Speaker Deck', 'title': 'Example',
            'url': 'https://speakerdeck.com/komagata/example', 'date': '2020-01-01',
            'slides': 10, 'thumbnail': './images/example.jpg',
        }]}
        (site / 'catalog.json').write_text(json.dumps(catalog))
        (site / 'private.pdf').write_text('must not publish')
        (site / '.oma-approved-validation').write_text('must not publish')
        return web, manifest

    def run_build(self, root, output):
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--output', str(output)], capture_output=True, text=True)

    def test_only_selected_assets_are_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            output = root / '_site'
            result = self.run_build(root, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            files = [p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()]
            self.assertEqual(len(files), 62)
            self.assertEqual(sum(p.endswith('.png') for p in files), 38)
            self.assertEqual(sum(p.endswith('.mp4') for p in files), 4)
            self.assertFalse(any('validation' in p or p.endswith(('.pdf', '.md')) or 'unused' in p for p in files))
            self.assertEqual(
                {p.relative_to(output / 'omarchy-for-ai-era').as_posix()
                 for p in (output / 'omarchy-for-ai-era').rglob('*') if p.is_file()},
                {'index.html', 'images/icon.png', 'images/hardware/bg.webp',
                 'images/demo.mp4', 'images/poster.jpg'})
            self.assertEqual((output / 'omarchy-for-ai-era/index.html').read_bytes(),
                             (root / 'omarchy-for-ai-era/omarchy-for-ai-era.html').read_bytes())
            self.assertEqual(len(json.loads((output / 'ai-voice-assistant/slides.json').read_text())['slides']), 30)

    def test_second_marp_deck_copies_only_referenced_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            output = root / '_site'
            result = self.run_build(root, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            published = output / 'ore-no-omarchy-apps'
            self.assertEqual({p.relative_to(published).as_posix()
                              for p in published.rglob('*') if p.is_file()},
                             {'index.html', 'images/app.webp'})
            self.assertEqual((published / 'index.html').read_bytes(),
                             (root / 'ore-no-omarchy-apps/ore-no-omarchy-apps.html').read_bytes())
            self.assertEqual((published / 'images/app.webp').read_bytes(), b'app image')

    def test_invalid_marp_assets_preserve_previous_output(self):
        cases = ('images/missing.png', '../private.png', '/tmp/private.png',
                 'images/../../private.png', 'images/../private.png',
                 'https://example.com/a.png', '//example.com/a.png',
                 'images/%2e%2e/private.png', r'images/\private.png',
                 'images/icon.png?secret=1', 'images/private.md',
                 'images/icon.png#fragment', 'images/../../../omarchy-for-ai-era/images/icon.png')
        for reference in cases:
            with self.subTest(reference=reference), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                output = root / '_site'
                self.assertEqual(self.run_build(root, output).returncode, 0)
                before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
                (root / 'omarchy-for-ai-era/omarchy-for-ai-era.html').write_text(f'<img src="{reference}">')
                result = self.run_build(root, output)
                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertEqual(before, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_second_marp_unsafe_assets_preserve_previous_output(self):
        for markup in ('<img src="../private.png">',
                       '<img src="images/../../private.png">',
                       '<img src="images/missing.png">',
                       '<img src="https://example.com/a.png">',
                       '<img src="images/app.webp?secret=1">',
                       '<style>.a { background:url(//example.com/a.jpg) }</style>',
                       '<script src="images/private.js"></script>'):
            with self.subTest(markup=markup), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                output = root / '_site'
                self.assertEqual(self.run_build(root, output).returncode, 0)
                before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
                (root / 'ore-no-omarchy-apps/ore-no-omarchy-apps.html').write_text(markup)
                result = self.run_build(root, output)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(before, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_second_marp_symlink_assets_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            source = root / 'ore-no-omarchy-apps/images/app.webp'
            target = source.with_name('real.webp')
            source.rename(target)
            source.symlink_to(target.name)
            result = self.run_build(root, root / '_site')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Symlink in Marp asset:', result.stderr)
            self.assertFalse((root / '_site').exists())

    def test_marp_symlinks_rejected_even_inside_deck(self):
        for name in ('images/icon.png', 'images/hardware', 'omarchy-for-ai-era.html', 'images/quattro-4.5'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                output = root / '_site'
                self.assertEqual(self.run_build(root, output).returncode, 0)
                old = (output / 'omarchy-for-ai-era/index.html').read_bytes()
                source = root / 'omarchy-for-ai-era' / name
                target = source.with_name(source.name + '-real')
                source.rename(target)
                source.symlink_to(target.name, target_is_directory=target.is_dir())
                result = self.run_build(root, output)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((output / 'omarchy-for-ai-era/index.html').read_bytes(), old)

    def test_marp_runtime_remote_references_rejected(self):
        for markup in ('<video src="https://example.com/a.mp4"></video>',
                       '<video poster="//example.com/a.jpg"></video>',
                       '<div style="background:url(https://example.com/a.jpg)"></div>',
                       '<style>.a { background:url(https://example.com/a.jpg) }</style>',
                       '<script src="https://example.com/a.js"></script>',
                       '<link rel="stylesheet" href="https://example.com/a.css">',
                       '<base href="https://example.com/">'):
            with self.subTest(markup=markup), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                (root / 'omarchy-for-ai-era/omarchy-for-ai-era.html').write_text(markup)
                self.assertNotEqual(self.run_build(root, root / '_site').returncode, 0)
                self.assertFalse((root / '_site').exists())

    def test_artifact_budget_retains_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            output = root / '_site'
            self.assertEqual(self.run_build(root, output).returncode, 0)
            before = (output / 'index.html').read_bytes()
            # Sparse file exercises the pre-copy bound without writing a huge fixture.
            with (root / 'omarchy-for-ai-era/images/demo.mp4').open('wb') as video:
                video.truncate(100_000_000)
            result = self.run_build(root, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('100 MB budget', result.stderr)
            self.assertEqual((output / 'index.html').read_bytes(), before)

    def test_reordered_videos_are_published_at_their_source_positions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            output = root / '_site'
            result = self.run_build(root, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((output / 'ai-voice-assistant/slides.json').read_text())
            self.assertEqual([(i, s['video']) for i, s in enumerate(data['slides'], 1) if 'video' in s], [
                (11, 'videos/OMA-PV.mp4'),
                (13, 'videos/ヘイ、オーマあなたは何ですか.mp4'),
            ])

    def test_required_vendor_files_are_copied_exactly_and_repeat_build_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            web, _ = self.fixture(root)
            output = root / '_site'
            result = self.run_build(root, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            vendor = output / 'ai-voice-assistant/vendor/reveal'
            self.assertTrue((vendor / 'reveal.js').is_file(), 'Required reveal.js was not published')
            self.assertEqual({p.name for p in vendor.iterdir()}, {'reveal.js', 'reveal.css', 'reset.css', 'LICENSE'})
            for path in vendor.iterdir():
                self.assertEqual(path.read_bytes(), (web / 'vendor/reveal' / path.name).read_bytes())
            repeat = self.run_build(root, output)
            self.assertEqual(repeat.returncode, 0, repeat.stderr)

    def test_missing_or_escaping_vendor_file_rejected_before_publication(self):
        for name in ('reveal.js', 'reveal.css', 'reset.css', 'LICENSE'):
            for kind in ('missing', 'escape'):
                with self.subTest(name=name, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    web, _ = self.fixture(root)
                    source = web / 'vendor/reveal' / name
                    source.unlink()
                    if kind == 'escape':
                        private = root / 'private.txt'
                        private.write_text('private')
                        source.symlink_to(private)
                    output = root / '_site'
                    result = self.run_build(root, output)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Missing or unsafe viewer file:', result.stderr)
                    self.assertFalse(output.exists())

    def test_rejects_unsafe_missing_and_malformed_references(self):
        cases = ('/tmp/private.png', '../private.png', 'slides/../../private.png', 'https://example.com/x.png', 'slides/missing.png', 'slides/%2e%2e/private.png')
        for path in cases:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                web, manifest = self.fixture(root)
                manifest['slides'][0]['image'] = path
                (web / 'slides.json').write_text(json.dumps(manifest))
                result = self.run_build(root, root / '_site')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Build failed:', result.stderr)
                self.assertFalse((root / '_site').exists())

    def test_missing_video_and_unsafe_overlay_fail_before_publication(self):
        for kind in ('missing-video', 'unsafe-overlay', 'wrong-count'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                web, manifest = self.fixture(root)
                if kind == 'missing-video':
                    (root / 'ai-voice-assistant/videos/OMA-PV.mp4').unlink()
                elif kind == 'unsafe-overlay':
                    manifest['slides'][10]['overlay_image'] = '../private.png'
                else:
                    manifest['slides'].pop()
                (web / 'slides.json').write_text(json.dumps(manifest))
                result = self.run_build(root, root / '_site')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Build failed:', result.stderr)
                self.assertFalse((root / '_site').exists())

    def test_output_symlink_cannot_redirect_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            destination = root / 'other'
            destination.mkdir()
            output = root / '_site'
            output.symlink_to(destination, target_is_directory=True)
            result = self.run_build(root, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Build failed:', result.stderr)
            self.assertEqual(list(destination.iterdir()), [])

    def test_repository_deck_builds_with_two_videos_and_no_absolute_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'site'
            result = self.run_build(ROOT, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((output / 'ai-voice-assistant/slides.json').read_text())
            self.assertEqual(len(data['slides']), 30)
            self.assertEqual([(i, s['video']) for i, s in enumerate(data['slides'], 1) if 'video' in s], [
                (11, 'videos/OMA-PV.mp4'),
                (13, 'videos/ヘイ、オーマあなたは何ですか.mp4'),
            ])
            self.assertNotIn('/tmp/', json.dumps(data))
            page = (output / 'index.html').read_text()
            self.assertEqual(page.count('class="card"'), 36)
            self.assertEqual(page.count('href="./ore-no-omarchy-apps/"'), 1)
            self.assertEqual((output / 'ore-no-omarchy-apps/index.html').read_bytes(),
                             (ROOT / 'ore-no-omarchy-apps/ore-no-omarchy-apps.html').read_bytes())
            self.assertIn('href="./catalog.css"', page)
            self.assertIn('src="./catalog.js"', page)
            self.assertIn('id="catalog-controls" hidden', page)
            self.assertNotIn('{{CARDS}}', page)
            self.assertEqual(len(list((output / 'images').glob('*.jpg'))), 35)
            self.assertLess(sum(p.stat().st_size for p in output.rglob('*') if p.is_file()), 100_000_000)


if __name__ == '__main__':
    unittest.main()
