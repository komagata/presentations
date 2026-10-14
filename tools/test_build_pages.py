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
            if number in (10, 12):
                name = 'ヘイ、オーマあなたは何ですか.mp4' if number == 10 else 'OMA-PV.mp4'
                (videos / name).write_bytes(b'mp4')
                slide.update(video=f'videos/{name}', span=True, loop=False, muted=False)
            slides.append(slide)
        manifest = {'title': 'AI Voice Assistant', 'slides': slides}
        (web / 'slides.json').write_text(json.dumps(manifest))
        for path in ('export.pdf', 'validation.html', 'README.md'):
            (web / path).write_text('must not publish')
        (videos / 'unused.mp4').write_bytes(b'unused')
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
            self.assertEqual(len(files), 41)
            self.assertEqual(sum(p.endswith('.png') for p in files), 30)
            self.assertEqual(sum(p.endswith('.mp4') for p in files), 2)
            self.assertFalse(any('validation' in p or p.endswith(('.pdf', '.md')) or 'unused' in p for p in files))
            self.assertEqual(len(json.loads((output / 'ai-voice-assistant/slides.json').read_text())['slides']), 30)

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
                    manifest['slides'][9]['overlay_image'] = '../private.png'
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
            self.assertEqual([i for i, s in enumerate(data['slides'], 1) if 'video' in s], [10, 12])
            self.assertNotIn('/tmp/', json.dumps(data))
            self.assertLess(sum(p.stat().st_size for p in output.rglob('*') if p.is_file()), 30_000_000)


if __name__ == '__main__':
    unittest.main()
