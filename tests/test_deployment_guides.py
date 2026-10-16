import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('brand_audit', ROOT / 'scripts/audit_brand.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class BrandPolicyTests(unittest.TestCase):
    def check_text(self, text, name='guide.md'):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / name).write_text(text)
            return audit.audit(tmp)

    def test_installable_tree(self):
        self.assertEqual(audit.audit(ROOT / 'skills')['issues'], [])

    def test_display_case_variants(self):
        for token in ('HAP', 'HaP', 'hap-brand', 'Mingdao', '明道雲'):
            with self.subTest(token=token):
                self.assertTrue(self.check_text(token)['issues'])

    def test_technical_names_and_false_positives(self):
        result = self.check_text('HAP-Appid HAP-Appkey HAP-Sign hap hap-cli hap_cli HAP_PROFILE shape batchApprove spc&happ')
        self.assertEqual(result['issues'], [])
        self.assertEqual(sum(result['counts'].values()), 7)

    def test_old_filename(self):
        self.assertTrue(self.check_text('niio', 'Hap-guide.md')['issues'])

    def test_migration_exception_scoped(self):
        self.assertTrue(self.check_text('hap-plan.json')['issues'])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/audit.MIGRATION
            p.parent.mkdir(parents=True)
            p.write_text('hap-plan.json hap-context.json')
            self.assertEqual(audit.audit(tmp)['issues'], [])

    def test_generated_guides_match_reviewed_overrides(self):
        import json
        base=ROOT/'localization/overrides/deployment-guides'
        for item in json.loads((base/'manifest.json').read_text()):
            with self.subTest(path=item['target']):
                self.assertEqual((base/item['target']).read_bytes(), (ROOT/'skills'/item['target']).read_bytes())

if __name__ == '__main__':
    unittest.main()
