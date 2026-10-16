import hashlib
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SampleImagesTests(unittest.TestCase):
    def test_reviewed_catalog_and_references(self):
        manifest=json.loads((ROOT/'localization/image-catalog.json').read_text())['images']
        catalog=json.loads((ROOT/'skills/mcp/niio-mcp-app-builder/build/resources/sample_images.json').read_text())
        entries=[e for group in catalog.values() for e in group]
        expected={e['file']:e for e in manifest if e.get('enabled',True)}
        self.assertEqual(len(entries),len(expected))
        self.assertEqual({e['url'].rsplit('/',1)[-1] for e in entries},set(expected))
        for e in entries:
            name=e['url'].rsplit('/',1)[-1];source=expected[name]
            self.assertTrue(e['url'].startswith('https://raw.githubusercontent.com/apsm-niio/niio-skills/main/assets/sample-images/'))
            self.assertEqual(hashlib.sha256((ROOT/'assets/sample-images'/name).read_bytes()).hexdigest(),source['sha256'])
            if 'keywordOverride' in source:self.assertEqual(e['keyword'],source['keywordOverride'])
        self.assertNotIn('asset-015.jpg',expected)
if __name__=='__main__':unittest.main()
