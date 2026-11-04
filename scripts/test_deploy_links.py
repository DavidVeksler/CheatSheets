"""Regression: generated Worker pages resolve, missing links still fail.

python -m unittest scripts.test_deploy_links -v
"""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import deploy


class GeneratedRouteLinks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.patch = patch.object(deploy, 'ROOT', str(self.root))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def check(self, href, page='example.html'):
        dest = self.root / page
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f'<a href="{href}">Link</a>', encoding='utf-8')
        return deploy.check_links([page])

    def test_known_routes_require_their_sources(self):
        self.assertTrue(self.check('popularity'))
        (self.root / 'popularity.php').write_text('<?php echo "traffic";')
        self.assertEqual(self.check('popularity'), [])
        self.assertEqual(self.check('/popularity?days=7#chart'), [])
        self.assertTrue(self.check('sitemap.xml'))
        (self.root / 'sitemap.php').write_text('<?php echo "sitemap";')
        self.assertEqual(self.check('/sitemap.xml'), [])

    def test_unknown_and_wrong_directory_links_still_fail(self):
        (self.root / 'popularity.php').write_text('<?php echo "traffic";')
        self.assertTrue(self.check('missing-page'))
        self.assertTrue(self.check('popularity', 'nested/example.html'))
        self.assertTrue(self.check('/popularity/'))
        self.assertEqual(self.check('/popularity', 'nested/example.html'), [])


if __name__ == '__main__':
    unittest.main()
