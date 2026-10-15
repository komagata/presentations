"""Catalog content and offline publication safety tests."""
from collections import Counter
from copy import deepcopy
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
import tempfile
import unittest

import test_build_pages

ROOT = test_build_pages.ROOT


class CatalogTest(unittest.TestCase):
    fixture = test_build_pages.PackagingTest.fixture
    run_build = test_build_pages.PackagingTest.run_build

    def test_repository_inventory_preserves_every_external_record(self):
        catalog = json.loads((ROOT / 'site/catalog.json').read_text())
        entries = catalog['presentations']
        self.assertEqual(len(entries), 34)
        self.assertEqual(len({p['id'] for p in entries}), 34)
        self.assertEqual(Counter(p['source'] for p in entries), {'Local': 2, 'Speaker Deck': 18, 'SlideShare': 14})
        self.assertTrue(all(p['source'] == 'Local' and p['date'] is None for p in entries[:2]))
        # Separate platform records remain even when their titles match.
        self.assertEqual(sum(p['title'] == '漬け水に浸かる' for p in entries), 2)
        external = []
        for entry in entries[2:]:
            original = {key: entry[key] for key in ('id', 'source', 'title', 'url', 'slides', 'date')}
            original['thumbnail'] = entry['thumbnail_url']
            external.append(original)
        fingerprint = hashlib.sha256(json.dumps(sorted(external, key=lambda p: p['id']), ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertEqual(fingerprint, '75c978e3b20205a001f3549e4bf622bf4182bc127848133b1f3a5d60ad0a8db5')

    def test_ssr_cards_escape_metadata_and_keep_subpath_relative_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / 'site/catalog.json'
            data = json.loads(path.read_text())
            data['presentations'][0]['title'] = '<script>" & title'
            local = deepcopy(data['presentations'][0])
            local.update(id='local-ai', source='Local', date=None, url='./ai-voice-assistant/',
                         thumbnail='./ai-voice-assistant/slides/slide-001.png')
            data['presentations'].append(local)
            path.write_text(json.dumps(data))
            output = root / '_site'
            result = self.run_build(root, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            page = (output / 'index.html').read_text()
            self.assertEqual(page.count('class="card"'), 2)
            self.assertIn('&lt;script&gt;&quot; &amp; title', page)
            self.assertNotIn('<script>"', page)
            self.assertIn('href="./ai-voice-assistant/"', page)
            self.assertIn('src="./ai-voice-assistant/slides/slide-001.png"', page)
            before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
            self.assertEqual(self.run_build(root, output).returncode, 0)
            self.assertEqual(before, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_invalid_metadata_never_replaces_previous_output(self):
        cases = [
            {'url': 'javascript:alert(1)'}, {'url': '//speakerdeck.com/x'},
            {'url': 'https://speakerdeck.com.evil.test/x'},
            {'url': 'https://user@speakerdeck.com/x'}, {'url': 'https://speakerdeck.com:444/x'},
            {'thumbnail_url': 'javascript:alert(1)'},
            {'thumbnail_url': 'https://cdn.slidesharecdn.com/wrong-source.jpg'},
            {'thumbnail': '../private.jpg'}, {'thumbnail': './images/../private.jpg'},
            {'thumbnail': './images/%2e%2e.jpg'}, {'thumbnail': './images/missing.jpg'},
            {'source': 'Other'}, {'slides': True}, {'slides': 0}, {'date': '2026-99-99'},
            {'id': '../bad'}, {'title': ''}, {'unknown': 'field'},
        ]
        for change in cases:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                output = root / '_site'
                self.assertEqual(self.run_build(root, output).returncode, 0)
                old = (output / 'index.html').read_bytes()
                path = root / 'site/catalog.json'
                data = json.loads(path.read_text())
                data['presentations'][0].update(change)
                path.write_text(json.dumps(data))
                result = self.run_build(root, output)
                self.assertNotEqual(result.returncode, 0, change)
                self.assertEqual((output / 'index.html').read_bytes(), old)

    def test_duplicate_id_and_symlink_escape_rejected(self):
        for kind in ('duplicate', 'image', 'template', 'catalog'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                path = root / 'site/catalog.json'
                if kind == 'duplicate':
                    data = json.loads(path.read_text())
                    data['presentations'].append(deepcopy(data['presentations'][0]))
                    path.write_text(json.dumps(data))
                else:
                    source = root / 'site' / {'image': 'images/example.jpg', 'template': 'index.html', 'catalog': 'catalog.json'}[kind]
                    private = root / 'private.txt'
                    private.write_bytes(source.read_bytes())
                    source.unlink()
                    source.symlink_to(private)
                self.assertNotEqual(self.run_build(root, root / '_site').returncode, 0)
                self.assertFalse((root / '_site').exists())

    def test_source_output_collision_and_unrelated_output_rejected(self):
        for name in ('site', 'site/output', 'ai-voice-assistant', 'other'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                if name == 'other':
                    (root / name).mkdir()
                    (root / name / 'secret.txt').write_text('private')
                result = self.run_build(root, root / name)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((root / 'site/catalog.json').exists())

    @unittest.skipUnless(shutil.which('node'), 'Node is needed for the JS behavior check')
    def test_combined_search_source_filters_count_and_empty_state(self):
        script = r'''const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const entries = JSON.parse(fs.readFileSync(process.argv[1], 'utf8')).presentations;
const elements = {};
for (const id of ['catalog-controls', 'search', 'source', 'result-count', 'empty-state']) {
  elements[id] = { hidden: true, value: '', listeners: {}, addEventListener(event, callback) { this.listeners[event] = callback; } };
}
elements.source.value = 'all';
const cards = entries.map(p => ({ dataset: { source: p.source, title: p.title }, hidden: false }));
const document = {
  getElementById: id => elements[id],
  querySelectorAll: selector => selector === '.card' ? cards : [],
};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), { document });
const count = () => cards.filter(c => !c.hidden).length;
assert.equal(elements['catalog-controls'].hidden, false);
assert.equal(count(), 34);
for (const [source, expected] of [['Local', 2], ['Speaker Deck', 18], ['SlideShare', 14]]) {
  elements.source.value = source;
  elements.source.listeners.change();
  assert.equal(count(), expected);
  assert.equal(elements['result-count'].textContent, `${expected}件 / 34件`);
}
elements.source.value = 'all';
elements.search.value = '漬け水に浸かる';
elements.search.listeners.input();
assert.equal(count(), 2);
elements.source.value = 'SlideShare';
elements.source.listeners.change();
assert.equal(count(), 1);
elements.search.value = 'a-title-that-does-not-exist';
elements.search.listeners.input();
assert.equal(count(), 0);
assert.equal(elements['empty-state'].hidden, false);
elements.source.value = 'Local';
elements.search.value = '  ＡＩ  ';
elements.search.listeners.input();
assert.equal(count(), 1);
assert.equal(elements['empty-state'].hidden, true);
elements.search.value = '';
elements.source.value = 'all';
elements.source.listeners.change();
assert.equal(count(), 34);
'''
        result = subprocess.run(['node', '-e', script, str(ROOT / 'site/catalog.json'), str(ROOT / 'site/catalog.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
