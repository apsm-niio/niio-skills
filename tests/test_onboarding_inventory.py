import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from onboarding_inventory import inventory


class InventoryTests(unittest.TestCase):
    def fixture(self, root):
        for i in reversed(range(8)):
            p = root / 'skills' / ('mcp' if i % 2 else 'api') / f'niio-test-{i}'
            p.mkdir(parents=True)
            (p / 'SKILL.md').write_text(f'---\nname: niio-test-{i}\n---\n', encoding='utf-8')
            for j in range(i):
                (p / f'{j}.txt').write_text('sample', encoding='utf-8')

    def test_names_keep_counts_and_hashes_together(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            result = inventory(root)
            for i in range(8):
                row = result['skills'][f'niio-test-{i}']
                self.assertEqual(row['fileCount'], i + 1)
                self.assertEqual(len(row['sha256']), i + 1)
            self.assertEqual(result['totalFiles'], 36)

    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            p = root / 'skills/extra/niio-test-0'
            p.mkdir(parents=True)
            (p / 'SKILL.md').write_text('---\nname: niio-test-0\n---\n')
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                inventory(root)

    def test_name_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            next(root.glob('skills/*/*/SKILL.md')).write_text('---\nname: wrong\n---\n')
            with self.assertRaisesRegex(ValueError, 'does not match'):
                inventory(root)

    def test_powershell_encoding_risk(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            (root / 'bad.ps1').write_text("Write-Host '中文'", encoding='utf-8')
            (root / 'bom.ps1').write_text("Write-Host '中文'", encoding='utf-8-sig')
            (root / 'ascii.ps1').write_text("Write-Host 'OK'", encoding='ascii')
            risk = {x['path']: x['nonAsciiWithoutUtf8Bom'] for x in inventory(root)['powershell']}
            self.assertEqual(risk, {'ascii.ps1': False, 'bad.ps1': True, 'bom.ps1': False})

    def test_missing_skill_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'eight'):
                inventory(d)


if __name__ == '__main__':
    unittest.main()
